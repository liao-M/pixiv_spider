最开始写这个爬虫是觉得每次自己去p站扒图好蠢，于是想自己写一个。

只是可惜我的python水平实在抠脚，写了两个下午才写了个雏形出来，借鉴了不少网上的经验，比如下载原图时要加入的referer.下载速度很慢，而且暂时只能下载单图，正在考（xue）虑（xi）加入多线程。

我的想法是除了第一次下载所有图片外，以后每次都只下载新出现的作品。我的基本想法是，每次先爬有多少作品，保存在一个txt里，然后每次打开爬虫的时候进行对比就好了，可是我发现照我这种每个页面爬一遍然后统计总数的方法来做的话实在太慢了。。。但是坑爹的p站没有尾页这一说法，我暂时也想不出来什么好办法。

目前的代码也很丑，乱得很，下次写多线程的时候重构（写）一下吧

暂时就这么写吧，好蠢(｡ŏ_ŏ)

#### todo list
- [ ] 重构
- [ ] 多线程
- [ ] 错误处理
- [ ] 图形界面
