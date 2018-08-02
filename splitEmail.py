import jieba,os,chardet,time,collections,pickle
class SplitEmail:
    def __init__(self):
        self.word_dir = {"normal":{},"trash":{}}
        '''
        {
            "normal":{
                1:['你好','公司','广告'],
                2:['公司','领导','公关']
            },
            "trash":{
                1:['你好','公司','广告'],
                2:['公司','领导','公关']
            }
        }
        '''
        self.word_list = {"normal":[],"trash":[]}
        """
        {
            "normal":['你好','公司','广告','公司','领导','公关'],
            "trash":['你好','公司','广告','公司','领导','公关']
        }
        """
    def splitEmailByjieba(self,files):
        for typ in os.listdir(files):
            fn = files + typ
            for fname in os.listdir(fn):
                filename = fn+"/"+fname
                with open(filename,encoding="gb2312",errors="ignore") as f:
                    con = f.read()
                    index = con.index("\n\n")
                    con = con[index::]
                    res = list(set(jieba.cut(con)))
                    self.word_list[typ]+=res
                    if fname not in self.word_dir[typ]:
                        self.word_dir[typ][fname] = res

    def getNTRatio(self,typ):
        '''
        每个分词 在其对应邮件中的概率
        如果有10份邮件 含有“公司”的邮件为5  概率为50%
        '''

        counter = collections.Counter(self.word_list[typ])
        # ['你好', '公司', '广告', '公司', '领导', '公关']
        # {"公司":2,"你好":1,"广告":1}

        dic = collections.defaultdict(list)
        # {"公司":[2],'你好':1}


        for word in counter:
            dic[word].append(counter[word])

        #dic {"公司":[2/],'你好':[1]}
        #邮件总数
        count = len(self.word_dir[typ])

        for key in dic:
            dic[key][0] = dic[key][0]/count
        
        return dic

    def getRatio(self):
        trash_ratio = self.getNTRatio("trash")
        # { "公司":[0.25]}
        normal_ratio = self.getNTRatio("normal")
        # { "公司":[0.32],"领导":[0.02]}
        ratio = normal_ratio
        #{"公司":[0.32,0.25],"领导":[0.02]}
        for word in trash_ratio:
            if word in ratio:
                ratio[word].append(trash_ratio[word][0])
            else:
                num = trash_ratio[word][0]
                ratio[word] = [0.01,num]

        
        #单词只在正常中有
        for word in ratio:
            if len(ratio[word])==1:
                ratio[word].append(0.01)
        
        return ratio
        #{"公司":[0.32,0.25],"领导":[0.02,0.01]}

def main():
    demo = SplitEmail()
    demo.splitEmailByjieba("./data/")
    ratio = demo.getRatio()
    with open("ratio.txt","ab+") as f:
        pickle.dump(ratio,f)
    
if __name__ == "__main__":
    main()
    
