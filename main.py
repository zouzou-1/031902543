#-*- conding:utf-8 -*-
from io import DEFAULT_BUFFER_SIZE
import re
import json
import sys
import copy
MinMatchType = 1 # 最小匹配规则
MaxMatchType = 2 # 最大匹配规则
matched_sensitivewords=dict()
matched_sensitivewords_list=list()
read_file_name=list()


# 按行读取txt文件
def readtxt(file_name):
    with open(file_name, 'r',encoding='utf-8') as file_to_read:
        lines = list()
        for line in file_to_read.readlines():
            if line is not None:
                lines.append(line.strip('\n'))
    file_to_read.close()       
    return lines

#创建文件
#写入文件中的一行
#构建敏感词库

class sensitive_class(object):
    

    def __init__(self):
        #找出敏感词
        #file_to_read=input()
        #file_to_read='C:/Users/zy/Documents/Tencent Files/791275445/FileRecv/个人编程作业/words.txt'
        sensitive_words_list=readtxt(str(read_file_name[1]))#按地址读入敏感词文件，并转化为列表
        self.root = dict()#初始化字典
        #一个一个列表元素加入字典
        for word in sensitive_words_list:
            self.add_word(word)

        

    def add_word(self, word):

        now_node = self.root#从根节点开始
        word_count = len(word)#字符串长度

        # 无意义词库,在检测中需要跳过的（这种无意义的词最后有个专门的地方维护，保存到数据库或者其他存储介质中）
        self.skip_root = [' ', '&', '!', '！', '@', '#', '$', '￥', '*', '^', '%', '?', '？', '<', '>', "《", '》','_','+','-','*','(',')','|']

        
        for i in range(word_count):
            char_str = word[i]
            if char_str in now_node.keys():
                # 如果存在该key，直接赋值，用于下一个循环获取
                now_node = now_node.get(word[i])
                now_node['is_end'] = False
            else:
                # 不存在则构建一个dict
                new_node = dict()
 
                if i == word_count - 1:  # 最后一个
                    new_node['is_end'] = True
                else:  # 不是最后一个
                    new_node['is_end'] = False
 
                now_node[char_str] = new_node

                now_node = new_node


    def check_match_word(self,line, begin_index, match_type=MinMatchType):
        
        flag = False
        match_flag_length = 0  # 匹配字符的长度
        now_map = self.root
        tmp_flag = 0  # 包括特殊字符的敏感词的长度
        str=''
        flag_h=0
        for i in range(begin_index, len(line)):
            word = line[i]
        
            # 检测是否是特殊字符"
            if word in self.skip_root and flag_h:
                # len(nowMap)<100 保证已经找到这个词的开头之后出现的特殊字符
                tmp_flag += 1
                continue
            # 获取指定key
            if 'a' <= line[i-1] <= 'z' and '0'<=word <='9' and flag_h:
                tmp_flag += 1
                continue

            if 'A' <= line[i-1] <= 'Z' and '0'<=word <='9' and flag_h:
                tmp_flag += 1
                continue
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
        if tmp_flag < 2 or not flag:  # 长度必须大于等于1，为词
            tmp_flag = 0
        #if str:
            #print(str)
        return [tmp_flag,str]



    def test_in_line(self,line, match_type=MinMatchType):
        """
        获取匹配到的词语
        :param txt:待检测的文本
        :param match_type:匹配规则 1：最小匹配规则，2：最大匹配规则
        :return:文字中的相匹配词
        """
        matched_word_list = list()
        matched_sensitivewords_list.clear()
        for i in range(len(line)):  # 0---11
            length= self.check_match_word(line, i, match_type)
            if length[0] > 0:
                word = line[i:i + length[0]]
                matched_word_list.append(word)
                # i = i + length - 1
                matched_sensitivewords_list.append(length[1])
        
        return matched_word_list


    
    def test_for_sensitivewords(self):
        
        print_out=dict()
        #file_to_read='C:/Users/zy/Documents/Tencent Files/791275445/FileRecv/个人编程作业/org.txt'
        wait_for_test_list=readtxt(str(read_file_name[2]))#按地址读入待检测文件，并按行转化为列表
        count=0#初始化行数记录
        count_1=0
        for line in wait_for_test_list:
            count+=1#从第一行开始检测
            print_out[count]=self.test_in_line(line,MinMatchType)#调用检测函数
            matched_sensitivewords[count]=copy.copy(matched_sensitivewords_list)
            if len(print_out[count]):
                count_1+=len(print_out[count])
            
       
        #f=open('C:/Users/zy/Documents/Tencent Files/791275445/FileRecv/个人编程作业/ans1.txt','w') 
        f=open(str(read_file_name[3]),'w')
        f.write('Total: '+str(count_1)+'\n')
        for i in range(1,len(print_out)):
            w=print_out[i]
            c=matched_sensitivewords[i]
            #print(c)
            t=len(w)
            j=0
            if t>0:
                while( j < t):
                   
                    f.write('Line'+str(i)+": <"+c[j]+"> "+w[j]+'\n')
                    #print("Line:",str(i),"<",c[j],">",w[j])测试输出
                    j+=1
            
if __name__=='__main__':
    
    for i in sys.argv:
        read_file_name.append(str(i))
    
       
    #构建敏感词词库：
    sensitive_map=sensitive_class()
    #调用敏感词检测函数：
    sensitive_map.test_for_sensitivewords()
 
