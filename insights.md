pre-game tcp + 多线程

game 多进程





login不成功，server就主动断开链接

后续修改：

1. 消息队列，因为可能收到的消息不是当前程序想要的
2. register发邮件验证码
3. 服务器端验证客户是否已经走到某一个step，防止客户端欺骗

协议原则：action关键字唯一确定一个action， 同一种action对应唯一一个处理函数

面向对象：保存作为对象instance的数据必须是正确的合法的

计算分布：能放在client的就放在client，因为一并放在sever就要加上网络延时也加重server负担



如果无法连接服务器，异常处理

有的错误比如网络错误不应该让程序中断

有的错误比如编程的时候数据库查询语句写错，应该让程序中断

调试信息选择显示，异常信息必显示

Client.send()异常处理

每个gui做完修改后都将数据保存在client中

如果操作合法，服务器端进行数据修改并返回相应字符串，如果不合法，服务器端不修改数据，返回相应字符串

只要是error都print出来

一条异常信息首先需要展示出来，其次需要处理这个异常，本函数处理调用函数的异常，本函数的异常异常交给引用者处理

搞清楚什么是异常（客观因素，主观无法解决），什么是结果的一种

如果是一个非常基础的函数，异常处理交给调用函数，如果是一个顶端的函数，异常处理自己做

请求能判断的首先在客户端判断，然后再在服务器判断，有时客户端的交互逻辑已经隐含请求判断

client编程思路：一个gui写一个class，class中同时实现gui使用的方法，若有必要，给方法分配线程，client在连接成功后就分配一个线程一直监听。

gui面向对象编程，Card，Cards，

server判断输赢，用修饰器

gui与底层数据分离		

每个object在创建时就有自己的主人(每个object都是由自己的主人创建的, object的转移在主人处有具体的方法, 转移的时候重新display, display是把所有属于这个主人的object进行展示)

