# py_package_tool
> python package tool script.


## 必需(限制)



* 必须保证autoxml可执行文件和generateAPK文件夹在同级目录
* 项目resguard.gradle文件白名单下必须加入如下，否则无法反编译apk:
    
```
            "R.style.yh_bottom_select",
            "R.attr.*",
            "R.color.subject_color",
            "R.color.custom_notification_layout_color",
            "R.drawable.startload_page_picture_new",
            "R.string.app_name",
            "R.string.SERVER_HOST",
            "R.string.SERVER_HOST_TEMP",
            "R.string.RETRIEVE_HOST",
            "R.string.RETRIEVE_HOST_TEMP"
```

**2.1.0版本及以上支持域名及皮肤根据包名自动匹配替换，显然皮肤(color、drawable)资源也需要加入白名单.**

* 必须保证微信回调已用activity别名的方式替换（**微信回调的两个activity只使用一套，其它渠道下的src下的微信回调可删除**），如下:

    ![image](https://github.com/keernice/py_package_tool/raw/master/IMG/8.jpg)
    
    


## 说明

1. 直接下载package_script使用即可，解压缩后目录分为两部分autoxml(可执行文件)和generateAPK文件夹，如下图

	![目录](https://github.com/keernice/py_package_tool/blob/master/IMG/1.png)
	
2. 双击autoxml可执行文件执行打包任务之前需要做一些准备工作,如下:

    ![](https://github.com/keernice/py_package_tool/blob/master/IMG/2.png)
    
    * generateAPK/apks目录下：通过AndroidStudio打好的apk放入此目录下，命名没有限制
    * generateAPK/pics目录下：图片文件资源目录，用来替换apk中的图片资源文件
    > 目前配置中只支持应用图标、启动页loading图两个资源的替换
        
    * generateAPK/config.xml: **打包配置文件，这是重点！！！** 后面详细介绍


3. 其它目录
    * generateAPK/apkOut: 放置apk反编译后的文件目录
    * generateAPK/recompileApk: 放置通过config配置完成资源替换打包的apk目录

## config.xml打包配置文件

![](https://github.com/keernice/py_package_tool/blob/master/IMG/3.png)

XML配置文件以<decompile></decompile>元素标签作为打包一个apk的基本配置单位；<decompile>下的子元素标签见名知意，配置好标签元素对应的资源内容或名称(针对图片资源替换，需要填入pics下准备好的资源文件名称)，脚本会加载配置文件，根据配置完成apk中资源内容替换。

1. application-id 标识包名
2. theme 标识主题颜色，即：
    * subject-color对应colors.xml中name=“subject_color”的颜色资源
    * notification-color对应colors.xml中name=“custom_notification_layout_color”的颜色资源
    * 如果不需要做主题颜色的替换工作，可如下设置(满足如下其中一种即可)：
        
        * isReplace属性设置为false，反之则是需要替换主题颜色
        * 删除<theme>元素
        * 当theme元素存在且isReplace为true时，如果subject-color和notification-color元素都没有值或者不存在，也是不执行替换工作的
    
3. app-name 标识应用名称
4. app-icon 标识应用图标
5. splash-icon 标识应用启动页启动图
6. app-version 标识应用版本号，即VersionCode；**注意：**因为没有加入VersionName，脚本程序自动使用‘.’分割VersionCode生成VersionName，即331会自动生成versionname为3.3.1，请打包人员评估打包需求中的版本号是否兼容。
    
    > 错误示例：打包需求VersionCode和VersionName不一样时配置无效
    
7. umeng-channel 标识友盟渠道号，多渠道号可用逗号‘,’隔开，兼容中英文逗号
8. domain-group 标识域名组
        
    ![](https://github.com/keernice/py_package_tool/blob/master/IMG/4.png)
        
    > **上图string字符串字符串，需要手动加入到项目strings.xml中**

    * server-host 标识SERVER_HOST
    * server-host-temp 标识SERVER_HOST_TEMP
    * retrieve-host 标识RETRIEVE_HOST
    * retrieve-host-temp 标识RETRIEVE_HOST_TEMP
        
    项目中如下图调用，ServerDomain.java文件需要下载下来放到项目中：
        
    * 在MyApplication中加入如下方法
        
    ![](https://github.com/keernice/py_package_tool/blob/master/IMG/5.png)
        
    * 所有调用BuildConfig.SERVER_HOST、BuildConfig.SERVER_HOST_TEMPBuildConfig.RETRIEVE_HOST、BuildConfig.RETRIEVE_HOST_TEMP的地方需要更改为MyApplication.getHost()使用，如下举例：
            
    ![](https://github.com/keernice/py_package_tool/blob/master/IMG/6.png)
    
    1. app-version-name  标识android:VersionName
            
## 可能会出现的问题

1. apk文件覆盖问题
    ![](https://github.com/keernice/py_package_tool/blob/master/IMG/7.png)
    
    **如果配置xml中两个decompile元素中除了theme、app-version、domain-group元素值不同，其它元素值相同(另:两个decompile元素下的umeng-channel子元素中也不能包含相同的渠道号)，就会导致打好的apk包发生覆盖问题，请注意此问题**
            
1. windows平台下若双击运行出错可使用powershell运行

## Version 2.1.0版本更改详细说明

![](https://github.com/keernice/py_package_tool/blob/master/IMG/10.png)


config.xml配置文件删除了标签<theme/>、<domain_group/>
新增<app-theme/>、<domain_switch>标签
### 支持皮肤根据包名自动替换

![](https://github.com/keernice/py_package_tool/blob/master/IMG/14.png)

1. resource文件夹
    
    * 新版本支持皮肤根据包名自动匹配替换的功能,resource文件夹用来存储皮肤，即app项目下，与main同级的分发渠道文件夹，如下图：


        ![](https://github.com/keernice/py_package_tool/blob/master/IMG/11.png)

    * 是否开启皮肤根据包名自动替换功能，需要在config.xml配置文件中使用<app-theme isReplace=“true”>来声明，默认isReplace值为false，即不开启皮肤替换功能.
2. resource_mapping.xml 皮肤资源映射配置文件,如下图:


![](https://github.com/keernice/py_package_tool/blob/master/IMG/12.png)


包名与对应皮肤资源文件夹的映射如上，applicationID标识包名,type标识皮肤资源文件夹。

### 支持域名根据包名自动替换

config.xml配置文件中提供<domain_switch>标签，标识是否开启域名组根据包名自动替换，默认false不开启.

1. domain_config.xml域名组配置文件，如下图

![](https://github.com/keernice/py_package_tool/blob/master/IMG/13.png)

2. domain_mapping.xml包名与域名组映射配置文件，如下图

![](https://github.com/keernice/py_package_tool/blob/master/IMG/9.png)

 
 








## 功能特性

* 支持自动化反编译apk、替换资源、回包apk
* 兼容mac、windows平台
* 支持xml配置替换资源
* 支持package_name替换
* 支持app图标替换
* 支持启动图替换
* 支持app_name替换
* 支持友盟渠道号替换
* 支持域名组替换
* 支持皮肤替换(包括主题color、drawable)
* 支持versionName替换
* 支持双击可执行文件运行，脱离命令行,不需要安装python环境



## 发布历史

### Version 2.1.0

* 支持皮肤根据包名自动匹配替换
* 支持域名根据包名自动匹配替换


### Version 2.0.1

* 支持versionName替换


### Version 2.0
* 配置文件使用xml替换json(match.json-->config.xml),功能逻辑发生了比较大的改变
* 增加umeng_channel渠道号更改功能
* 增加app_version应用版本号更改功能
* 增加域名组更改功能,即SERVER_HOST、SERVER_HOST_TEMP、RETRIEVE_HOST、RETIEVE_HOST_TEMP的更改
* 更好的异常处理机制
* 优化删除冗余



### Version 1.0.2
1. 支持apk主题色更改
2. 支持apk启动页启动图更改
3. match.json匹配文件结构优化
4. 优化异常输出(警告、错误格式化背景输出)
5. 修复若干bug


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
