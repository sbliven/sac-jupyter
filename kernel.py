from queue import Queue
from threading import Thread

from ipykernel.kernelbase import Kernel
import re
import subprocess
import tempfile
import os
import os.path as path
import json
import shlex

import ctypes

def rm_nonempty_dir (d):
    for root, dirs, files in os.walk (d, topdown=False):
        for name in files:
            os.remove (os.path.join(root, name))
        for name in dirs:
            os.rmdir (os.path.join(root, name))
    os.rmdir (d)


class RealTimeSubprocess(subprocess.Popen):
    """
    A subprocess that allows to read its stdout and stderr in real time
    """

    def __init__(self, cmd, write_to_stdout, write_to_stderr, directory):
        """
        :param cmd: the command to execute
        :param write_to_stdout: a callable that will be called with chunks of data from stdout
        :param write_to_stderr: a callable that will be called with chunks of data from stderr
        """
        self._write_to_stdout = write_to_stdout
        self._write_to_stderr = write_to_stderr

        super().__init__(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0, cwd=directory)

        self._stdout_queue = Queue()
        self._stdout_thread = Thread(target=RealTimeSubprocess._enqueue_output, args=(self.stdout, self._stdout_queue))
        self._stdout_thread.daemon = True
        self._stdout_thread.start()

        self._stderr_queue = Queue()
        self._stderr_thread = Thread(target=RealTimeSubprocess._enqueue_output, args=(self.stderr, self._stderr_queue))
        self._stderr_thread.daemon = True
        self._stderr_thread.start()

    @staticmethod
    def _enqueue_output(stream, queue):
        """
        Add chunks of data from a stream to a queue until the stream is empty.
        """
        for line in iter(lambda: stream.read(4096), b''):
            queue.put(line)
        stream.close()

    def write_contents(self):
        """
        Write the available content from stdin and stderr where specified when the instance was created
        :return:
        """

        def read_all_from_queue(queue):
            res = b''
            size = queue.qsize()
            while size != 0:
                res += queue.get_nowait()
                size -= 1
            return res

        stdout_contents = read_all_from_queue(self._stdout_queue)
        if stdout_contents:
            self._write_to_stdout(stdout_contents)
        stderr_contents = read_all_from_queue(self._stderr_queue)
        if stderr_contents:
            self._write_to_stderr(stderr_contents)


class SacKernel(Kernel):
    implementation = 'jupyter_sac_kernel'
    implementation_version = '0.1'
    language = 'sac'
    language_version = 'SaC-1.2'
    language_info = {'name': 'sac',
                     'mimetype': 'text/plain',
                     'file_extension': '.sac'}
    banner = "SaC kernel.\n" \
             "Uses sac2c, to incrementaly compile the notebook.\n"
    def __init__(self, *args, **kwargs):
        super(SacKernel, self).__init__(*args, **kwargs)
        self.files = []
        self.stmts = []
        self.imports = [
            #"use StdIO: all;",
            #"use Array: all;"
        ]
        self.funs = []
        self.sac2c_flags =  ['-v0', '-O0', '-noprelude', '-noinl', '-specmode', 'aud']

        p = '/home/tema/src/sac2c-jupyter-modified'
        self.sac2c_bin = p + '/build_r/sac2c_p'
        self.sac2c_so = p + '/build_r/lib/libsac2c_p.so'
        self.sac2c_so_handle = ctypes.CDLL (self.sac2c_so, mode=(1|ctypes.RTLD_GLOBAL))
        self.sac2c_so_handle.jupyter_init ()
        
        #self.sac2c_so_handle.parse_from_string.argtypes = []
        self.sac2c_so_handle.parse_from_string.restype = ctypes.c_void_p

        self.sac2c_so_handle.jupyter_free.argtypes = ctypes.c_void_p,
        self.sac2c_so_handle.jupyter_free.res_rtype = ctypes.c_void_p


        # Creatae the directory where all the compilation/execution will be happening.
        self.tmpdir = tempfile.mkdtemp (prefix="jup-sac")

    def cleanup_files(self):
        """Remove all the temporary files created by the kernel"""
        for file in self.files:
            os.remove(file)

        # Remove the directory
        rm_nonempty_dir (self.tmpdir)
    
        # Call some cleanup functions in sac2c library.
        self.sac2c_so_handle.jupyter_finalize ()

    def check_sacprog_type (self, prog):
        s = ctypes.c_char_p (prog.encode ('utf-8'))
        ret_ptr = self.sac2c_so_handle.parse_from_string (s, -1) #len (self.imports))
        ret_s = ctypes.cast (ret_ptr, ctypes.c_char_p).value
        self.sac2c_so_handle.jupyter_free (ret_ptr)
        #print ("received json {}".format (ret_s))
        j = {"status": "fail", "stderr": "cannot parse json: {}".format (ret_s)}
        try:
            j = json.loads (ret_s)
        except:
            pass
        return j

            

    def new_temp_file(self, **kwargs):
        """Create a new temp file to be deleted when the kernel shuts down"""
        # We don't want the file to be deleted when closed, but only when the kernel stops
        kwargs['delete'] = False
        kwargs['mode'] = 'w'
        kwargs['dir'] = self.tmpdir
        file = tempfile.NamedTemporaryFile(**kwargs)
        self.files.append(file.name)
        return file

    def _write_to_stdout(self, contents):
        self.send_response(self.iopub_socket, 'stream', {'name': 'stdout', 'text': contents})

    def _write_to_stderr(self, contents):
        self.send_response(self.iopub_socket, 'stream', {'name': 'stderr', 'text': contents})

    def create_jupyter_subprocess(self, cmd):
        return RealTimeSubprocess(cmd,
                                  lambda contents: self._write_to_stdout(contents.decode()),
                                  lambda contents: self._write_to_stderr(contents.decode()),
                                  self.tmpdir)

    #def compile_with_gcc(self, source_filename, binary_filename, cflags=None, ldflags=None):
    #    cflags = ['-std=c11', '-fPIC', '-shared', '-rdynamic'] + cflags
    #    args = ['gcc', source_filename] + cflags + ['-o', binary_filename] + ldflags
    #    return self.create_jupyter_subprocess(args)
    
    def compile_with_sac2c(self, source_filename, binary_filename, extra_flags=[]):
        # Flags are of type list of strings.
        sac2cflags = self.sac2c_flags + extra_flags 
        args = [self.sac2c_bin] + ['-o', binary_filename] + sac2cflags + [source_filename]
        return self.create_jupyter_subprocess(args)


    # def _filter_magics(self, code):

    #     magics = {'cflags': [],
    #               'ldflags': [],
    #               'args': []}

    #     for line in code.splitlines():
    #         if line.startswith('//%'):
    #             key, value = line[3:].split(":", 2)
    #             key = key.strip().lower()

    #             if key in ['ldflags', 'cflags']:
    #                 for flag in value.split():
    #                     magics[key] += [flag]
    #             elif key == "args":
    #                 # Split arguments respecting quotes
    #                 for argument in re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', value):
    #                     magics['args'] += [argument.strip('"')]

    #     return magics
    def check_magics (self, code):
        print (code.splitlines ())
        lines = code.splitlines ()
        if len (lines) < 1:
            return 0
        l = lines[0].strip ()
        if l == '%print':
            return self.mk_sacprg ("/* Placeholder.  */ 0", 1)
        elif l == '%flags':
            return ' '.join (self.sac2c_flags)
        elif l.startswith ('%setflags'):
            nl = shlex.split (l[len ('%setflags'):])
            self.sac2c_flags = nl
            return "setting flags to: {}".format (nl)
        elif l == '%help':
            return """\
Currently the following commands are available:
    %print      -- print the current program including
                   imports, functions and statements in the main.
    %flags      -- print flags that are used when running sac2c.
    %setflags <flags>
                -- reset sac2c falgs to <flags>
"""
        else:
            return None



    def mk_sacprg (self, txt, r):

        stmts = "\n\t".join (self.stmts)
        funs = "\n\n".join (self.funs)
        imports = "\n".join (self.imports)

        if r == 1: # expr
            stmts += "StdIO::print ({}\n\n);".format (txt)

        elif r == 2: # stmt
            stmts += txt

        elif r == 3: # fundef
            funs += txt

        else: # use/import/typedef
            imports += txt


        prg = """\
// use/import/typedef
{}

// functions
{}

// main function with stmt.
int main () {{
    {}
    return 0;
}}
"""
        p = prg.format (imports, funs, stmts)
        #print ("---\n", p)
        return p

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        
        #print ("user_expressions = ", user_expressions)
        #magics = self._filter_magics(code)

        m = self.check_magics (code)
        if m is not None:
            self._write_to_stdout (m)
            return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [],
                    'user_expressions': {}}


        r = self.check_sacprog_type (code)
        if r["status"] != "ok": # == -1:
            self._write_to_stderr(
                    "[SaC kernel] This is not an expression/statements/function or use/import/typedef\n"
                    + r["stderr"])
            return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [],
                    'user_expressions': {}}


        with self.new_temp_file(suffix='.sac') as source_file:
            source_file.write(self.mk_sacprg (code, r["ret"]))
            source_file.flush()
            with self.new_temp_file(suffix='.exe') as binary_file:
                p = self.compile_with_sac2c(source_file.name, binary_file.name) 
                #, magics['cflags'], magics['ldflags'])
                while p.poll() is None:
                    p.write_contents()
                p.write_contents()
                if p.returncode != 0:  # Compilation failed
                    self._write_to_stderr(
                            "[SaC kernel] sac2c exited with code {}, the executable will not be executed".format(
                                    p.returncode))
                    return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [],
                            'user_expressions': {}}

        p = self.create_jupyter_subprocess([binary_file.name]) # + magics['args'])
        while p.poll() is None:
            p.write_contents()
        p.write_contents()

        if p.returncode != 0:
            self._write_to_stderr("[SaC kernel] Executable exited with code {}".format(p.returncode))
        else:
            if r["ret"] == 2: # stmts
                self.stmts.append (code)
            elif r["ret"] == 3: # funs
                self.funs.append (code)
            elif r["ret"] == 4: # use/import/typedef
                self.imports.append (code)

        return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}

    def do_shutdown(self, restart):
        """Cleanup the created source code files and executables when shutting down the kernel"""
        self.cleanup_files()


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=SacKernel)
