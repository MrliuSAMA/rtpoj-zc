rtpoj-zc Means Root Zone Project-(Zone Communication)

v0.1

---脚本信息

chkrr.py
利用dig工具校验资源记录集,完成数据元素的获取和校验

debuginfo.py
将打印调试信息的功能封装到一个模块中,不必每次打印信息时重复写各种类型的print.
每种类型的数据的打印都封装成一句话的函数

fc.py
主功能函数,被chkrr.py调用,用于打印优化后的调试信息

argument_input.py
用于将协约内容标准化为json格式的文件,半自动的小插件

argument2queryfile.py
用于从标准化的json文件中,提取出脚本想要自动获取并校验的查询


---文件IO

root.key
校验查询采用的锚文件,一个数据发布的服务器对应一个锚文件

queryfile
chkrr.py的输入文件,用于批处理查询,查询的结果存储在queryfile.result中

queryfile.result
保存queryfile的查询结果







