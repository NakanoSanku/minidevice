#!/bin/sh
sdk=$(getprop ro.build.version.sdk)
vmsize=$(wm size | awk -F":" '{gsub(/ /, "", $2); print $2}')
abi=$(getprop ro.product.cpu.abi)
echo "SDK版本：$sdk"
echo "屏幕分辨率：$vmsize"
echo "CPU架构：$abi"
if (($sdk >33))
then
    echo "设备不符合要求"
    exit 1
else
    echo "设备符合要求"
fi
# 设置GitHub的URL
github_url="https://github.com"

# 发送HTTP GET请求并获取返回状态码
status_code=$(curl --head --silent --output /dev/null --write-out "%{http_code}" $github_url)
githubProxyUrl=""
# 检查返回状态码
if (( $status_code == 200 )); then
    echo "设备可以连通GitHub。"
else
    echo "设备无法连通GitHub。"
    githubProxyUrl="https://ghproxy.com/"
    status_code=$(curl --head --silent --output /dev/null --write-out "%{http_code}" $githubProxyUrl)
    if (( $status_code == 200 )); then
    echo "代理网址可用"
        break
    else
        echo "代理网址不可用"
        githubProxyUrl=""
    fi
    echo "麻痹的,你这什么垃圾网络"
    if (( $0 >0 ));then
    echo "自己去找个Github代理api 形如:https://ghproxy.com/"
    echo "请输入api地址:"
    read githubProxyUrl
    fi
fi

minicapUrl="${githubProxyUrl}https://raw.githubusercontent.com/NakanoSanku/minidevice/master/minidevice/bin/minicap"
minitouchUrl="${githubProxyUrl}https://raw.githubusercontent.com/NakanoSanku/minidevice/master/minidevice/bin/minitouch/libs"

# 下载并安装 minicap
minicapDir="/data/local/tmp/minicap"
minicapSoDir="/data/local/tmp/minicap.so"
curl -o "${minicapDir}" "${minicapUrl}/libs/${abi}/minicap"
curl -o "${minicapSoDir}" "${minicapUrl}/jni/android-${sdk}/${abi}/minicap.so"
chmod +x "${minicapDir}"

# 下载并安装 minitouch
minitouchDir="/data/local/tmp/minitouch"
curl -o "${minitouchDir}" "${minitouchUrl}/${abi}/minitouch"
chmod +x "${minitouchDir}"

echo "minicap和minitouch安装完成。"
