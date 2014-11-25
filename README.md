## Baidu-FE-Code-Style

Baidu FE Code Style 是一个基于[fecs](https://github.com/ecomfe/fecs)开发的 Sublime Text 2/3 和 WebStorm 插件，目的是方便的验证所写的代码是否符合 [百度前端编码规范](https://github.com/ecomfe/spec) 的要求

## Sublime Text 2/3

### 安装

#### 手工安装

1. git checkout https://github.com/leeight/Baidu-FE-Code-Style.git 'Baidu FE Code Style'
2. 把 'Baidu FE Code Style' 目录放到
   1. OS X: ~/Library/Application Support/Sublime Text 2/Packages
   2. Windows: %APPDATA%\Sublime Text 2\Packages
   3. Linux: ~/.config/sublime-text-2/Packages

#### 通过Package Control安装

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

点击圆点之后，具体的 warning 信息会显示在底部的状态栏，如果错误信息太多，状态栏显示不全的话，可以通过`Ctrl + ~`调用 Sublime Text 的 Console，里面有更详细的信息。

## WebStorm

### 安装

WebStorm默认集成了`jscs`的插件，我们只需要修改一下配置即可使用，首先需要通过`npm i -g fecs`来确保系统中已经安装了`fecs`，然后修改`jscs`的配置：

![webstorm-config.png](http://ecma.bdimg.com/adtest/webstorm-config-1bb84ea7.png)

主要是修改`JSCS Package`的路径。另外`Configuration file`和`Code style preset`可以随便选择，我们是用不到的（直接忽略了）

### 使用

配置之后就可以直接使用了，保存之后就会自动验证，效果如下：

![webstorm-result.png](http://ecma.bdimg.com/adtest/webstorm-result-c7aab9a3.png)
