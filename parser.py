"""
@theme: Parser
@source: 解析对应的文档需要对应的动词之类的原料

"""

from nltk.tree import Tree
from nltk.draw.tree import TreeView
from pyhanlp import *
import sys
sys.path.append("/Users/mario/Documents/OneDrive/GitHub/")
from PolicyReader.type import *
import re
import pandas as pd
import copy


class Preprocessor:
    def _symbol_remover(self,text):
        """ This method applies only on sentence, removing \\n too. """
        if not isinstance(text,list):
            text = [text]
            
        text = [re.sub("\\n|\\xa0|\\t|\\u0020|\\u00A0|\\u180E|\\u202f|\\u205f|\\u3000|\\u2000-\\u200B"," ",t) for t in text]
        text = [re.sub("\s+"," ",t) for t in text if len(t)>1]
        
        return text
    
    def _table_finder(self,text):
        """ This script helps find the latent table in the text. 
        
        * Example:
        -------- table --------
        车辆',
        '类型\t中央财政补贴标准',
        '（元/kWh）\t中央财政补贴调整系数\t中央财政单车补贴上限',
        '（万元）\t地方财政单车补贴',
        '\t\t\t6<L≤8m\t8＜L≤10m\tL>10m\t',
        '非快充类纯电动客车\t1800\t系统能量密度（Wh/kg）\t9\t20\t30\t不超过中央财政单车补贴额的50%',
        '\t\t85－95（含）\t95－115（含）\t115以上\t\t\t\t',
        '\t\t0.8\t1\t1.2\t\t\t\t',
        '快充类纯电动客车\t3000\t快充倍率\t6\t12\t20\t',
        '\t\t3C－5C（含）\t5C－15C（含）\t15C以上\t\t\t\t',
        '\t\t0.8\t1\t1.4\t\t\t\t',
        '插电式混合动力（含增程式）客车\t3000\t节油率水平\t4.5\t9\t15\t',
        '\t\t40%－45%（含）\t45%－60%（含）\u3000\t60%以上\t\t\t\t',
        '\t\t0.8\t1\t1.2\t\t\t\t',
        """
        if not isinstance(text,list):
            text = [text]
            
        table = []
        # use `\t` as the separator:
        return table,text
        
    
    def __init__(self,text):
        if not isinstance(text,list):
            text = [text]
                
        # before removing all the symbols, more details should be kept:
        # find available tables:
        self.tables,text = self._table_finder(text)
        text = self._symbol_remover(text)
        self.sentences = text


class TokenException(Exception):
    pass


class Tokenizer(Preprocessor):
    """ class: Tokenizer """
    def Phrase(self,text,encoding="utf8") -> list:
        self.encoding=encoding
        """
        * Description:
        Phrase :text: phrase the whole text into sentences
    
        * Argument:
        text: input textual data, better in list type."""
        try:
            filters = self.__FILTER__
        except:
            filters = []
        
        if not isinstance(text,list):
            text = [text]
        
        tokens = []
        for para in text:
        # split the whole text into the sentences
            para = re.sub('([。！？\?])([^”’])', r"\1\n\2", para)  # 单字符断句符
            para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号
            para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
            para = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
            # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
            para = para.rstrip()  # 段尾如果有多余的\n就去掉它
            # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
            res = [x for x in para.split("\n") if len(x)>=5 and x not in filters]
            res = list(set(res))
        
            if res:
                # only if this is not empty
                tokens += res
            else:
                next    
        # end for
        logger.info("[Tokenize] fetch %s paragraphs. "%len(tokens))
        if tokens:
            return tokens
        else:
            raise TokenException("Empty token received.")
        
        
    def Segment(self,text) -> list:
        """ Tokenize one sentence into word tokens """
        segs = HanLP.segment(text)
        wordArray = []
        for each in segs:
            wordArray += [each.toString().split("/")]
        # end for
        return wordArray
    
    
    def IndexedSegment(self,sentences) -> dict:
        index = []
        for s in sentences:
            index += [self.Segment(s)]
        # end for
        return index
        
        
    def __init__(self,*args):
        args = list(args)        
        self.__FILTER__ = []
        self.__RAWTEXTS__ = args       
        # active instances:
        self.sentences = self.Phrase(args)
        super(Tokenizer, self).__init__(self.sentences)
        # indexed sentences:
        self.indexedSegments = self.IndexedSegment(self.sentences)
        

class Parser(Tokenizer,Verb,Rhetoric,Entity,Time,Department):
    def __init__(self,doc):
        """ Parser: a generalised method of parsing texts and transform them
        into desirable forms - array: [sentence:[tokens:]]
        *Parameters:
            :doc: Document object, with .content attribute
        """
        string = doc.content
        # super allows the __init__ to prepare the string and tokenize it
        super(Parser, self).__init__(string)
        doc.sentences = self.sentences
        doc.indexedSegments = self.indexedSegments
        
    
    def retriveEntity(self):
        """  """
        pass
    
    
    
    def retriveTime(self):
        pass
    
        
    def parse(self):
        """ select verbs and pipe them into Verb class
        *Attributes:
            .sentences: raw sentences
            .indexSegements: pos-tag list
        """
        
        """ word parse: pos-tag analysis """
        
        # :verb
        # v::动词 vd::副动词	vf::趋向动词	vg::动词性语素	vi::不及物动词（内动词）	
        # vl::动词性惯用语	 vn::名动词	vshi::动词“是”	vx::形式动词	vyou::动词“有”
        _verbalRef = ["v","vd","vf","vg","vi","vl","vn","vx"] # remove shi and you
        # :rhetoric
        _adjRef = ["a","ad","an","ag","al"]
        _advRef = ["d"]
                
        VERB,RHETORIC,OTHER = [],[],[]
        VOCAB = {}
        for sentence in self.indexedSegments:
            verb,rhetoric,other = [],[],[]
            for token in sentence:
                if VOCAB.get(token[1]):
                    if token[1] not in VOCAB[token[1]]:
                        VOCAB[token[1]] += [token[0]]
                else:
                    VOCAB[token[1]] = [token[0]]
                    
                if token[1] in _verbalRef:
                    verb += [Verb(token[0],token[1])]
                    
                elif token[1] in (_adjRef+_advRef):
                    rhetoric += [Rhetoric(token[0],token[1])]
                else:
                    other += token
            # end for
            if verb:
                VERB += [verb]
            if rhetoric:
                RHETORIC += [rhetoric]
            if other:
                OTHER += [other]
        # end for
        self.other = OTHER
        # update Document:
        doc.vocab = VOCAB
        doc.rhetoric = RHETORIC
        doc.verb = VERB
        
        """ entity parse: retrieve entities """
        # retrieve by verbal words:
        
        
        
        
        """ time parse: recognise Time """
        
        
        
        return doc
        
    
class DependencyParser:
    """ class: dependency-based parser
    Example: 调整新能源汽车推广应用财政补贴政策
    
    """
    def _hanlp_find_dependencyChildren(self,dep,start):
        stack = [start]
        ladder = {}
        while True:
            try:
                one = stack.pop()
            except:
                break
            
            ladder["%s_%s"%(one.LEMMA,one.ID)] = {}
            for each in list(dep.findChildren(one)):
                ladder["%s_%s"%(one.LEMMA,one.ID)]["%s_%s"%(each.LEMMA,each.ID)] = each.DEPREL
            # end for
            stack += list(dep.findChildren(one))
        return ladder

    
    def query_by_relation(self,relation:dict = None,query:list=[]) -> dict:
        """ This query method helps collapse the dependency relation and return a dict:
        {"relation":...,"phrase":...}, where "phrase" is collapsed to be a sentence.
        
        * Argument:
        - relation: relation object in dict type
        - query: list of query relations
        """
        # get all items in relation dict:
        if not relation:
            relation = self.relation
        
        words = []
        stack = []
        if not query:
            for each in relation.values():
                for item in each:
                    words += list(item.values())
        else:
            for each in query:
                if each in relation.keys():
                    stack += relation[each]
                    for item in relation[each]:
                        words += list(item.values())
                        
        # collapse the phrase using the keys: `from` and `to`
        words = list(set(words))
        sortWords = {int(word.split("_")[-1]):word.split("_")[0] for word in words}
        sortWords = sorted(sortWords.items(),key=lambda x:x[0])
        _phrase = "".join([item[-1] for item in sortWords])
        # output:
        self.__QUERY__ = _phrase
        
        return _phrase
        
    
    def _default_parser(self,text: str) -> dict:
        """
        * Description:
        default parser based on Hanlp, details see at: https://github.com/hankcs/pyhanlp
        We call `HanLP` method here to manage the default dependency parsing.
        
        * Argument:
        - text: input text snippet into it
        
        * Return:
        return the dict object which contains the basic information in CoNLL format
        """
        self._default_text = text
        dep = HanLP.parseDependency(text)
        self.default_hanlpObject = dep
        
        # dep is a iterable object in JAVA format
        # dep's subset has the following keys: 
        # - CPOSTAG, DEPREL, HEAD, ID,  'LEMMA', 'NAME', 'NULL', 'POSTAG','ROOT'
        # use .findChildren(list(dep)[0]) to build the brace:
        conll_keys = ["ID","NAME","LEMMA","CPOSTAG","POSTAG","HEAD","DEPREL","DEPREL"]
        dict_conll = {}
        for key in conll_keys:
            dict_conll[key] = []
            for item in dep:
                if key != "HEAD":
                    dict_conll[key] += [item.__getattribute__(key)]
                else:
                    dict_conll[key] += [item.__getattribute__(key).ID]
        # parsed in dict
        self.default_dependency = dict_conll
        
        # preserve the format: DEPREL:{from: ID.LEMMA,to: HEAD.LEMMA}
        reltable = {rel:[] for rel in dict_conll["DEPREL"]}
        for index,item in enumerate(dict_conll["DEPREL"]):
            reltable[item] += [{"from":"%s_%s"%(dict_conll["LEMMA"][index],dict_conll["ID"][index]),"to":"%s_%s"%(dict_conll["LEMMA"][dict_conll["HEAD"][index] - 1],dict_conll["ID"][dict_conll["HEAD"][index] - 1])}]
            
        self.default_dependency_relation = reltable
        self.relation = reltable
        
        logger.info("[Default DepParser] Parse by HanLP.parseDependency: ")
        # display the dependency in tree plot:
        display(pd.DataFrame(dict_conll))
        
        # save self.dependencyString for drawing
        # example: '(ROOT(IP(NP(PN 我))(VP (VV 叫) (NP (NN 小米)))))' --> cfg
        # jpype._jclass.com.hankcs.hanlp.corpus.dependency.CoNll.CoNLLWord
        
        # pick the original and top item from dep:
        _start = list(dep)[dict_conll["DEPREL"].index("核心关系")]
        ladder = self._hanlp_find_dependencyChildren(dep,_start)
        # reverse the ladder, because the ladder follows the descending order:
        ladder_keys = list(ladder.keys())
        ladder_keys.reverse()
        
        temp = {}
        for item in ladder_keys:
            if not ladder.get(item):
                next
            else:
                child = ladder.get(item)
                _phrase = []
                for k,v in child.items():
                    if k in temp.keys():
                        _phrase += ["(%s %s)"%(v,temp[k])]
                    else:
                        _phrase += ["(%s %s)"%(v,k)]
                        
                temp[item] = item + " ".join(_phrase)
        # end for
        phrase = "(核心关系 %s)"%temp[ladder_keys[-1]]
        
        # output string:
        self.dependencyString = phrase
        
    
    def draw(self,img_outdir=None):
        """ Use NLTK method help visualize the dependency
        * Example:
            from nltk.tree import Tree
            demo = '(ROOT(IP(NP(PN 我))(VP (VV 叫) (NP (NN 小米)))))'
            Tree.fromstring(a).draw()
        """
        # to save the tree into image, see at: https://stackoverflow.com/questions/23429117/saving-nltk-drawn-parse-tree-to-image-file
        if self.dependencyString:
            tc = Tree.fromstring(self.dependencyString)
            if not img_outdir:
                img_outdir = "/"
            # output the image:
            # REMAIN: display of Chinese characters:
            if img_outdir:
                if not img_outdir.endswith('.ps'):
                    TreeView(tc)._cframe.print_to_file(img_outdir+"default_dependencyTree.ps")
                    sys_name = img_outdir+"default_dependencyTree.ps"
                else:
                    TreeView(tc)._cframe.print_to_file(img_outdir)
                    sys_name = img_outdir
            # end if
            
            # rebuild the file name and output:
            convert_name = "%s.png"%(sys_name.split(".")[0])
            out = os.system('convert %s %s'%(sys_name,convert_name))
            
            if out > 0:
                logger.error("[Dependency Draw] install ImageMagicK or the path is invaild. ")
            else:
                logger.info("[Dependency Parser] output tree image at [%s] "%convert_name)
                
            # return tc
            tc.pretty_print()
        
        
    def __init__(self):
        # provide default parsing:
        #self._default_parser(text)
        pass
        # in the future, we can provide more customized models for dependency parsing: