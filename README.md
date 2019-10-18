# py_package_tool
> python package tool script.


## features

* 支持自动化反编译apk、替换资源、回包apk
* 兼容mac、windows平台
* 支持xml配置替换资源
* 支持package_name替换
* 支持主题颜色替换
* 支持app图标替换
* 支持启动图替换
* 支持app_name替换
* 支持友盟渠道号替换
* 支持域名组替换
* 支持双击可执行文件运行，脱离命令行,不需要安装python环境


## 发布历史

### Version 2.0
* 配置文件使用xml替换json(match.json-->config.xml),功能逻辑发生了比较大的改变
* 增加umeng_channel渠道号更改功能
* 增加app_version应用版本号更改功能
* 增加域名组更改功能,即SERVER_HOST、SERVER_HOST_TEMP、RETRIEVE_HOST、RETIEVE_HOST_TEMP的更改
* 更好的异常处理机制
* 优化删除冗余


### Version 1.0.2
* 支持apk主题色更改
* 支持apk启动页启动图更改
* match.json匹配文件结构优化
* 优化异常输出(警告、错误格式化背景输出)



### Version 1.0.1
* 修复回编译时对apkOut目录遍历查询、判断是否与当前正在修改的apk名称相同时，recompile函数传入apkOutDirName参数错误
  导致无法回包bug.
* 修复'input('请按下任意键退出控制台窗口...')'每次回包完成时暂停的bug


### Version 1.0.0
* 支持apks文件夹目录下多包名遍历反编译、修改资源、回包流程
* 修复在mac下AutoPack和generateAPK只能放在用户目录下bug
* 优化异常堆栈信息打印
* 优化脚本流程逻辑
* 修复若干bug



### Version beta
- 上线 测试版python脚本打包
- 修复若干已知 bug
