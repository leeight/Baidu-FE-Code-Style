### Baidu-FE-Code-Style

Baidu FE Code Style 是一个基于[fecs](https://github.com/ecomfe/fecs)开发的 Sublime 2/3 插件，目的是方便的验证所写的代码是否符合 [百度前端编码规范](https://github.com/ecomfe/spec) 的要求

### 安装

#### 手工安装

1. git checkout https://github.com/leeight/Baidu-FE-Code-Style.git 'Baidu FE Code Style'
2. 把 'Baidu FE Code Style' 目录放到
   1. OS X: ~/Library/Application Support/Sublime Text 2/Packages
   2. Windows: %APPDATA%\Sublime Text 2\Packages
   3. Linux: ~/.config/sublime-text-2/Packages

#### 通过Package Control安装

> 注意：现在还不行，还需要等待发布

输入`Baidu FE Code Style`来进行查询，查询之后安装即可

### 配置

安装完毕之后，因为 Sublime 无法读取系统的`PATH`环境变量，所以初次使用需要配置一下相关的路径：

![fecs-config.png](http://ecma.bdimg.com/adtest/fecs-config-cf2d1959.png)

主要配置的内容如下（按照自己系统上的路径填写即可）：

```javascript
{
  "env": {
    "fecs_bin": "/usr/local/bin/fecs",
    "node_bin": "/usr/local/bin/node"
  }
}
```

### 使用

当打开一个`js`文件开始编辑，保存之后会自动调用`fecs`对当前的文件进行验证，如果有 warning 的话，会显示在左侧：

![fecs-show.png](http://ecma.bdimg.com/adtest/fecs-show-ba52dc3f.png)

点击圆点之后，具体的 warning 信息会显示在底部的状态栏
