import jieba,pickle,collections
class judgeEmail:
    def judge(self,email):
        res = list(set(jieba.cut(email)))
        
        for item in res:
            if item in  [',','，','.','。','(',')',':','：',"（","）","","\'","\"","”","[","]"," "," ","\n","\r","?","？","!","！","*","·","-","~",";","；","、","@"]:
                res.pop(res.index(item))
        
        with open("ratio.txt","rb+") as f:
            ratio = pickle.load(f)
       
        
        #{"公司":[0.25%,0.2%]}
        email_ratio = collections.defaultdict(list)

        for item in res:
            if item in ratio:
                email_ratio[item].append(ratio[item][0]) #把正常概率加进来
                email_ratio[item].append(ratio[item][1])#把不正常的概率加进来

        arr = sorted(email_ratio,key=lambda x:email_ratio[x][1],reverse = True)[0:15]
        print(arr)

        email_order_ratio = collections.defaultdict(list)
        
        for item in arr:
            email_order_ratio[item].append(email_ratio[item][0])
            email_order_ratio[item].append(email_ratio[item][1])
        print(email_order_ratio)

        p = 1.0
        #全概率
        rest_p = 1.0
        
        for item in email_order_ratio:
            #是垃圾邮件的概率
            p *=  email_order_ratio[item][1]
            #不是垃圾邮件的概率
            rest_p *= 1-email_order_ratio[item][1]
        P = p/(p+rest_p)
        
        info =""
        if P > 0.9:
            info = "垃圾邮件"
        else:
            info="正常邮件"
        return info,P,email_order_ratio
