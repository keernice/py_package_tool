# CHANGELOG


### Version 2.0
* 配置文件使用xml替换json(match.json-->config.xml),功能逻辑发生了比较大的改变
* 增加umeng_channel渠道号更改功能
* 增加app_version应用版本号更改功能
* 增加域名组更改功能,即SERVER_HOST、SERVER_HOST_TEMP、RETRIEVE_HOST、RETIEVE_HOST_TEMP的更改
* 更好的异常处理机制
* 优化删除冗余


## Version 1.0.3
1. 反编译后读取apk没有任何更改的原始资源 保证由于json配置项不完全，导致修改项被覆盖，
    读取原始资源用来还原apk在json中未配置修改项
2. 异常退出或跳过逻辑梳理  画uml逻辑流程图

## Version 1.0.2
1. 支持apk主题色更改
2. 支持apk启动页启动图更改
3. match.json匹配文件结构优化
4. 优化异常输出(警告、错误格式化背景输出)


## Version 1.0.0

1. 支持多包名apk遍历打包
2. 修改脚本路径为绝对路径，兼容mac windows，解决mac只能放在用户目录下使用
3. 更改match匹配文件格式为json，加强可读性、规避低级书写错误，并支持对json文件的扩展
4. 优化打包流程，打印异常堆栈信息
5. 修复app图标logo不兼容jpg、jpeg问题
6. 添加执行文件在控制窗口执行完成后不自动关闭逻辑
7. 修复apk文件name包含多个"."分隔符导致字符串切分错误
8. 支持自动分类不同母包名生成的子包
9. 优化字典及代码逻辑



## Version beta

1. 读取match文件:优化读取空行、无意义符号数据处理，兼容mac、windows平台
2. 解决windows平台下执行反编译、回包cmd命令进程挂起导致需手动继续问题，实现真正自动化
3. 排除mac系统文件夹下特有.DS_store隐藏文件对文件操作导致的解压缩异常
4. 优化字典中文件路径动态赋值
