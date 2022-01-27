(function(mod) {
  if (typeof exports == "object" && typeof module == "object"){ // CommonJS
    mod(require("codemirror/lib/codemirror"),
        require("codemirror/mode/clike/clike")
        );
  } else if (typeof define == "function" && define.amd){ // AMD
    define(["codemirror/lib/codemirror",
            "codemirror/mode/clike/clike"], mod);
  } else {// Plain browser env
    mod(CodeMirror);
  }
})(function(CodeMirror) {
    "use strict";

    function words(str) {
      var obj = {}, words = str.split(" ");
      for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
      return obj;
    }
    CodeMirror.defineMode("sac", function(conf, parserConf) {
        var cConf = {};
        for (var prop in parserConf) {
            if (parserConf.hasOwnProperty(prop)) {
                cConf[prop] = parserConf[prop];
            }
        }

        cConf.name = 'clike';
        cConf.keywords 
            = words ("if break case return default do else struct switch extern "
                    +"typedef for while const with genarray modarray fold "
                    +"module use import provide except all objdef class");
        cConf.types 
            = words ("int long char short byte uint ulong uchar ushort ubyte"
                    +"double float");
        cConf.blockKeywords
            = words("case do else for if switch while struct");
        //cConf.defKeywords: words("struct"),
        cConf.typeFirstDefinitions = true;
        cConf.atoms = words("true false");

        //hooks: {"#": cppHook, "*": pointerHook},
        //modeProps: {fold: ["brace", "include"]}


        return CodeMirror.getMode(conf, cConf);
    }, 'clike');

    CodeMirror.defineMIME("text/x-sac", "sac");
})

