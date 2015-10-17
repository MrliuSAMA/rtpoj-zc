#rtpoj-zc Means Root Zone Project

#####Zone Communication-v0.1.8  

##客户端  

###ChkRR.py

利用dig工具校验资源记录集,完成数据元素的获取和校验  
>调用  
>  
>debuginfo.py  
>将打印调试信息的功能封装到一个模块中,不必每次打印信息时重复写各种类型的print.
>每种类型的数据的打印都封装成一句话的函数  
>fc.py  
>主功能函数,被chkrr.py调用,用于打印优化后的调试信息  
>  
>IO(输入输出文件)  
>  
>queryfile.in  
>ChkRR.py的输入文件,用于批处理查询,查询的结果存储在queryfile.out中  
>queryfile.out  
>ChkRR.py的输出文件,保存queryfile.in的查询结果	  

###ArgumentInput.py

用于将协约内容标准化为json格式的文件,半自动的小插件  
>IO(输入输出文件)  
>  
>argument.in  
>采用json的格式保存协约内容,是ArgumentInput.py的输出  
 
###Argument2Queryfile.py

用于从标准化的json文件中,提取出脚本想要自动获取并校验的查询  
>IO(输入输出文件)  
>  
>argument.in  
>采用json的格式保存协约内容,是Argument2Queryfile.py的输入  
>queryfile.in  
>Argument2Queryfile.py的输出文件,用于批处理查询,是ChkRR.py的输入文件  


##服务器端  
<<<<<<< HEAD
  
###AutoConfig.py

=======

	* AutoConfig.py  
>>>>>>> 170dc5a22c9873543bf7090b20cd3a3b293dd84b
自动化的配置服务器，生成用于在bind上发布数据时使用的ZSK,KSK,ZoneDB,ZONESignedDB,NamedConf文件  
>调用  
>  
>debuginfo.py  
>将打印调试信息的功能封装到一个模块中,不必每次打印信息时重复写各种类型的print.  
>每种类型的数据的打印都封装成一句话的函数  
>  
>IO(输入输出文件)  
>  
>AutoConfig.py的输入文件,用于提供数据服务器的数据源



