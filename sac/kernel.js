
    //CodeMirror.defineSimpleMode("simplemode", {
    //  // The start state contains the rules that are intially used
    //  start: [
    //    // The regex matches the token, the token property contains the type
    //    {regex: /"(?:[^\\]|\\.)*?(?:"|$)/, token: "string"},
    //    // You can match multiple tokens at once. Note that the captured
    //    // groups must span the whole string in this case
    //    {regex: /(function)(\s+)([a-z$][\w$]*)/,
    //     token: ["keyword", null, "variable-2"]},
    //    // Rules are matched in the order in which they appear, so there is
    //    // no ambiguity between this one and the one above
    //    {regex: /(?:function|var|return|if|for|while|else|do|this)\b/,
    //     token: "keyword"},
    //    {regex: /true|false|null|undefined/, token: "atom"},
    //    {regex: /0x[a-f\d]+|[-+]?(?:\.\d+|\d+\.?\d*)(?:e[-+]?\d+)?/i,
    //     token: "number"},
    //    {regex: /\/\/.*/, token: "comment"},
    //    {regex: /\/(?:[^\\]|\\.)*?\//, token: "variable-3"},
    //    // A next property will cause the mode to move to a different state
    //    {regex: /\/\*/, token: "comment", next: "comment"},
    //    {regex: /[-+\/*=<>!]+/, token: "operator"},
    //    // indent and dedent properties guide autoindentation
    //    {regex: /[\{\[\(]/, indent: true},
    //    {regex: /[\}\]\)]/, dedent: true},
    //    {regex: /[a-z$][\w$]*/, token: "variable"},
    //    // You can embed other modes with the mode property. This rule
    //    // causes all code between << and >> to be highlighted with the XML
    //    // mode.
    //    {regex: /<</, token: "meta", mode: {spec: "xml", end: />>/}}
    //  ],
    //  // The multi-line comment state.
    //  comment: [
    //    {regex: /.*?\*\//, token: "comment", next: "start"},
    //    {regex: /.*/, token: "comment"}
    //  ],
    //  // The meta property contains global information about the mode. It
    //  // can contain properties like lineComment, which are supported by
    //  // all modes, and also directives like dontIndentStates, which are
    //  // specific to simple modes.
    //  meta: {
    //    dontIndentStates: ["comment"],
    //    lineComment: "//"
    //  }
    //});

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


  //function def(mimes, mode) {
  //  if (typeof mimes == "string") mimes = [mimes];
  //  var words = [];
  //  function add(obj) {
  //    if (obj) for (var prop in obj) if (obj.hasOwnProperty(prop))
  //      words.push(prop);
  //  }
  //  add(mode.keywords);
  //  add(mode.types);
  //  add(mode.builtin);
  //  add(mode.atoms);
  //  if (words.length) {
  //    mode.helperType = mimes[0];
  //    CodeMirror.registerHelper("hintWords", mimes[0], words);
  //  }

  //  for (var i = 0; i < mimes.length; ++i)
  //    CodeMirror.defineMIME(mimes[i], mode);
  //}

  //def(["text/x-sac"], {
  //  name: "clike",
  //  keywords: words("abstract as async await base break case catch checked class const continue" +
  //                  " default delegate do else enum event explicit extern finally fixed for" +
  //                  " foreach goto if implicit in interface internal is lock namespace new" +
  //                  " operator out override params private protected public readonly ref return sealed" +
  //                  " sizeof stackalloc static struct switch this throw try typeof unchecked" +
  //                  " unsafe using virtual void volatile while add alias ascending descending dynamic from get" +
  //                  " global group into join let orderby partial remove select set value var yield"),
  //  types: words("Action Boolean Byte Char DateTime DateTimeOffset Decimal Double Func" +
  //               " Guid Int16 Int32 Int64 Object SByte Single String Task TimeSpan UInt16 UInt32" +
  //               " UInt64 bool byte char decimal double short int long object"  +
  //               " sbyte float string ushort uint ulong"),
  //  blockKeywords: words("catch class do else finally for foreach if struct switch try while"),
  //  defKeywords: words("class interface namespace struct var"),
  //  typeFirstDefinitions: true,
  //  atoms: words("true false null"),
  //  hooks: {
  //    "@": function(stream, state) {
  //      if (stream.eat('"')) {
  //        state.tokenize = tokenAtString;
  //        return tokenAtString(stream, state);
  //      }
  //      stream.eatWhile(/[\w\$_]/);
  //      return "meta";
  //    }
  //  }
  //});


})

