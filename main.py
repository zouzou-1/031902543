#-*- conding:utf-8 -*-
import sys
import itertools
import copy
from xpinyin import Pinyin#需要安装一个模块


#绝大部分注释在代码上方
MinMatchType = 1 # 最小匹配规则
MaxMatchType = 2 # 最大匹配规则
matched_sensitivewords=dict()#敏感词对应字典
matched_sensitivewords_list=list()#敏感词对应列表
read_file_name=list()#存txt文件绝对地址的列表
expand_sensitivewords_list=list()#扩展敏感词过程中存放敏感词
result_matched=dict()#扩展后的敏感词，对应，最初给的敏感词（输出要用到）



# 按行读取txt文件：每行作为列表的一个元素
def readtxt(file_name):
    
    with open(file_name, 'r',encoding='utf-8') as f:
        lines = list()
        for line in f.readlines():
            if line is not None:
                lines.append(line.strip('\n'))
    f.close()       
    return lines

#拓展敏感词库(拼音和部分大小写情况)的类
class cartesian(object):
    def __init__(self,words):
        self._data_list=[]
        for word in words:
            self.expand_sensitivewords(word)
        self.build(words)
    #用于得到，例如['法','fa','f','F'],['F','f'],这样的列表
    def expand_sensitivewords(self,word):
        #汉字时
        if u'\u4e00' <= word <= u'\u9fff':
            p=Pinyin()
            py_all=p.get_pinyin(word)#全拼
            py_dhead=p.get_initial(word)#首字母
            py_xhead=py_dhead.lower()#小写首字母
            self.add_data([word,py_all,py_dhead,py_xhead])
        #字母时
        else:
            if 'a'<= word <='z':
                py_xhead=word
                py_dhead=word.upper()#转换大写
                self.add_data([word,py_dhead])

            else:
                py_xhead=word.lower()#转换小写  
                py_dhead=word
                self.add_data([word,py_xhead])
    #添加生成笛卡尔积的数据列表
    def add_data(self,data=[]): 
        self._data_list.append(data)
     #计算笛卡尔积，即得到'法轮gong'、'falungong'这样的字符串添加到敏感词字典里
    def build(self,words):
        for item in itertools.product(*self._data_list):
            str_1=''
            for word in item:
                str_1+=word
            result_matched[str_1]=words
            expand_sensitivewords_list.append(str_1)
            

#构建敏感词库和检测敏感词的类
class sensitive_class(object):

    def __init__(self):
        #按地址读入敏感词文件，并转化为列表
        sensitive_words_list=readtxt(str(read_file_name[1]))
        #初始化字典
        self.root = dict()
        #拓展敏感词
        for words in sensitive_words_list:
            car=cartesian(words)
        #一个一个列表元素加入字典
        for word in expand_sensitivewords_list:
            self.add_word(word)
    #将一个词加入敏感词字典函数    
    def add_word(self, word):
        #从根节点开始
        now_node = self.root
        #字符串长度
        word_count = len(word)
        # 汉字需要跳过的字符(这样区分为了实现汉字不穿插数字，字母穿插的要求，但是没有实现出来)
        self.skip_root = [' ', '&', '!', '！', '@', '#', '$', '￥', '*', '^', '%', '?', '？', '<', '>', "《", '》','_','+','-','*','(',')','|']
        # 数字需要跳过的字符
        self.szskip_root = [' ', '&', '!', '！', '@', '#', '$', '￥', '*', '^', '%', '?', '？', '<', '>', "《", '》','_','+','-','*','(',')','|','0','1','2','3','4','5','6','7','8','9']
        #字符串里一个一个字符顺序加入字典，构成一条链
        for i in range(word_count):
            char_str = word[i]
            if char_str in now_node.keys():
                # 如果存在该key，直接赋值，用于下一个循环获取
                now_node = now_node.get(word[i])
                now_node['is_end'] = False
            else:
                # 不存在则构建一个dict
                new_node = dict()
                # 最后一个
                if i == word_count - 1:
                    new_node['is_end'] = True
                # 不是最后一个
                else:  
                    new_node['is_end'] = False
 
                now_node[char_str] = new_node

                now_node = new_node

    #搜索是否配对的函数
    def search_match_word(self,line, begin_index, match_type=MinMatchType):
        
        flag = False
        # 匹配字符的长度
        match_flag_length = 0  
        now_map = self.root
        # 包括特殊字符的敏感词的长度
        tmp_flag = 0 
        #获取对应敏感词的，为了结果输出 
        str=''
        #标记该字符是否是敏感词中第一个字符
        flag_h=0
        #字符一次检测
        for i in range(begin_index, len(line)):
            word = line[i]
            # 检测是否是特殊字符且保证是已经找到这个词的开头之后出现的特殊字符
            if word in self.skip_root and flag_h:
                tmp_flag += 1
                continue 
            #获取字典中的KEY值，看是否匹配  
            now_map = now_map.get(word)
            if now_map:  # 存在，则判断是否为最后一个
                # 找到相应key，匹配标识+1
                flag_h=1
                match_flag_length += 1
                tmp_flag += 1
                # 如果为最后一个匹配规则，结束循环，返回匹配标识数
                if now_map.get("is_end"):
                    # 结束标志位为true
                    flag = True
                    # 最小规则，直接返回,最大规则还需继续查找
                    if match_type == MinMatchType:
                        str+=word
                        break
                str+=word      
            else:  # 不存在，直接返回
                str=''
                break
        if tmp_flag < 2 or not flag :  
            tmp_flag = 0
       
        return [tmp_flag,str]#返回的是待检测文中出现的字符串和对应的敏感词

    #待检测文本一行一行进入检测的函数
    def test_in_line(self,line, match_type=MinMatchType):
        #这是一个存一行里有多少个敏感词的列表，存入的是待检测文本里的敏感词
        matched_word_list = list()
        #这是一个存一行里有多少个敏感词的列表，存入的是待检测文本里的敏感词一一对应的敏感词库里的标准敏感词
        matched_sensitivewords_list.clear()
        for i in range(len(line)):
            #获取[待检测文本中敏感词长度，对应的标准敏感词]  
            length= self.search_match_word(line, i, match_type)
            if length[0] > 0:
                word = line[i:i + length[0]]
                matched_word_list.append(word)
                matched_sensitivewords_list.append(length[1])
        #返回一行中待检测文本里的敏感词列表
        return matched_word_list
    #开始检测文本的入口函数，检测从这个函数开始
    def test_for_sensitivewords(self):
        #存要输出数据的字典
        print_out=dict()
        #按地址读入待检测文件，并按行转化为列表
        wait_for_test_list=readtxt(str(read_file_name[2]))
        #初始化行数记录
        count=0
        #初始化检测出的敏感词数
        count_1=0
        #按行开始检测
        for line in wait_for_test_list:
            #从第一行开始检测
            count+=1
            #调用检测函数，print_out是待检测文本中的敏感词
            print_out[count]=self.test_in_line(line,MinMatchType)
            #matched_sensitivewords是待检测文本中的敏感词的对应标准敏感词
            matched_sensitivewords[count]=copy.copy(matched_sensitivewords_list)
            #记录检测敏感词数
            if len(print_out[count]):
                count_1+=len(print_out[count]) 
        #结果写入规定txt
        f=open(str(read_file_name[3]),'w')
        f.write('Total: '+str(count_1)+'\n')
        for i in range(1,len(print_out)):
            w=print_out[i]
            c=matched_sensitivewords[i]
            t=len(w)
            j=0
            if t>0:
                while( j < t):
                    f.write('Line'+str(i)+": <"+result_matched[c[j]]+"> "+w[j]+'\n')
                    j+=1
            
if __name__=='__main__':

    #命令行读入绝对地址

    if len(sys.argv) == 4:
        for i in sys.argv:
            read_file_name.append(str(i))
    else:
        print("检查一下输入")
        exit(0) 
    
    #构建敏感词词库：
    sensitive_map=sensitive_class()
    #调用敏感词检测函数：
    sensitive_map.test_for_sensitivewords()
 
