// 为 PreviewTextNode 添加显示文本功能的扩展脚本
import { app } from "../../scripts/app.js";
// 导入 ComfyWidgets
import { ComfyWidgets } from "../../scripts/widgets.js";

// 启用调试输出
const DEBUG = true;
function debug(...args) {
    if (DEBUG) console.log("[PreviewTextNode]", ...args);
}


// 当 ComfyUI 加载完毕后执行
app.registerExtension({
    name: "Styles.PreviewTextNode",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // 检查节点类型 (匹配多种可能的名称)
        if (nodeData.name === "Preview Text") {
            
            debug("找到预览文本节点:", nodeData.name);
            
            // 保存原始的 onNodeCreated 方法
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const ret = onNodeCreated
                    ? onNodeCreated.apply(this, arguments)
                    : undefined;

                debug("创建预览文本节点实例");
                
                try {
                    // 添加文本显示控件，使用 ComfyWidgets 如果可用，否则手动创建
                    if (typeof ComfyWidgets !== "undefined") {
                        const textWidget = ComfyWidgets.STRING(
                            this,
                            "display_text",
                            [
                                "STRING",
                                {
                                    default: "",
                                    placeholder: "文本输出显示...",
                                    multiline: true,
                                },
                            ],
                            app
                        );
                        
                        // 设置文本控件为只读
                        textWidget.widget.inputEl.readOnly = true;
                        
                        // 优化文本控件样式
                        textWidget.widget.inputEl.style.backgroundColor = "#1a1a1a";
                        textWidget.widget.inputEl.style.color = "#e0e0e0";
                        textWidget.widget.inputEl.style.fontFamily = "monospace";
                        textWidget.widget.inputEl.style.padding = "8px";
                        textWidget.widget.inputEl.style.border = "1px solid #333";
                        textWidget.widget.inputEl.style.borderRadius = "4px";
                        textWidget.widget.inputEl.style.height = "100%"; // 使用百分比高度
                        textWidget.widget.inputEl.style.minHeight = "60px"; // 最小高度
                        textWidget.widget.inputEl.style.resize = "none"; // 禁止手动调整大小
                        
                        // 储存对控件的引用，方便后续调整大小
                        this.textWidget = textWidget.widget;
                    } else {
                        // ComfyWidgets 不可用，使用替代方法
                        debug("ComfyWidgets不可用，使用替代方法");
                        // 创建一个基本的文本区域
                        this.addWidget("text", "display_text", "", (v) => {}, {
                            multiline: true,
                            readOnly: true
                        });
                        
                        // 获取刚刚添加的小部件，并应用样式
                        const widget = this.widgets[this.widgets.length - 1];
                        if (widget && widget.inputEl) {
                            widget.inputEl.style.backgroundColor = "#1a1a1a";
                            widget.inputEl.style.color = "#e0e0e0";
                            widget.inputEl.style.fontFamily = "monospace";
                            widget.inputEl.style.padding = "8px";
                            widget.inputEl.style.border = "1px solid #333";
                            widget.inputEl.style.borderRadius = "4px";
                            widget.inputEl.style.height = "100%"; // 使用百分比高度
                            widget.inputEl.style.minHeight = "60px"; // 最小高度
                            widget.inputEl.style.resize = "none"; // 禁止手动调整大小
                            
                            // 储存对控件的引用
                            this.textWidget = widget;
                        }
                    }
                } catch (error) {
                    console.error("创建文本控件时出错:", error);
                }

                // 调整节点大小
                this.setSize([this.size[0], Math.max(this.size[1], 150)]);
                app.graph.setDirtyCanvas(true, false);
                
                return ret;
            };
            
            // 重写 computeSize 方法，使节点能够调整大小
            const computeSize = nodeType.prototype.computeSize;
            nodeType.prototype.computeSize = function() {
                // 调用原始的 computeSize 方法
                const size = computeSize ? computeSize.apply(this) : [200, 100];
                
                // 返回计算好的大小
                return size;
            };
            
            // 重写 onResize 方法，处理节点大小变化
            const onResize = nodeType.prototype.onResize;
            nodeType.prototype.onResize = function(size) {
                // 调用原始的 onResize 方法
                if (onResize) {
                    onResize.apply(this, arguments);
                }
                
                // 调整文本控件大小以适应节点
                try {
                    const widget = this.textWidget || this.widgets.find(w => 
                        w.name === "display_text" || 
                        w.type === "text" || 
                        w.type === "customtext"
                    );
                    
                    if (widget && widget.inputEl) {
                        // 计算文本控件的新高度 (考虑节点标题和边距)
                        const titleHeight = 30; // 节点标题高度
                        const padding = 20; // 上下边距
                        const newHeight = size[1] - titleHeight - padding;
                        
                        // 设置控件高度
                        if (newHeight > 0) {
                            widget.inputEl.style.height = `${newHeight}px`;
                        }
                    }
                } catch (e) {
                    debug("调整控件大小时出错:", e);
                }
            };

            // 扩展节点执行后的处理
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                // 调用原始方法
                if (onExecuted) {
                    onExecuted.apply(this, arguments);
                }
                
                debug("执行结果:", message);
                
                // 初始化文本变量
                let textToDisplay = null;
                
                // 针对确定的消息格式，直接处理 UI 字符数组
                if (message && message.string && Array.isArray(message.string)) {
                    debug("直接处理已知的字符数组格式");
                    // 将字符数组转换为字符串
                    textToDisplay = message.string.join("");
                    // 应用特殊的逗号规则处理
                 
                        
                    debug("处理后文本:", textToDisplay);
                }
                // 如果直接处理失败，尝试其他可能的格式
                else {
                    try {
                        // 处理 UI 对象格式
                        if (message && message.ui) {
                            if (message.ui.string) {
                                debug("处理 ui.string 格式");
                                if (Array.isArray(message.ui.string)) {
                                  textToDisplay = message.ui.string.join("");
                                        
                                } else {
                                    textToDisplay = message.ui.string;
                                }
                            } else if (message.ui.text) {
                                debug("处理 ui.text 格式");
                                textToDisplay = message.ui.text;
                            }
                        }
                        // 处理其他简单格式
                        else if (typeof message === "string") {
                            debug("处理字符串消息");
                            textToDisplay = message;
                        }
                    } catch (e) {
                        debug("处理消息时出错:", e);
                    }
                }
                
                // 如果找到文本，更新显示
                if (textToDisplay !== null && textToDisplay !== undefined) {
                    // 安全地记录文本
                    debug(`显示文本 (${typeof textToDisplay}):`);
                    if (typeof textToDisplay === "string") {
                        debug(textToDisplay.substring(0, 50) + "...");
                    } else {
                        debug(String(textToDisplay));
                    }
                    
                    // 确保文本是字符串
                    if (typeof textToDisplay !== "string") {
                        textToDisplay = String(textToDisplay);
                    }
                    
                    // 查找文本控件
                    let textWidget = null;
                    
                    // 方法1: 查找指定名称的控件
                    textWidget = this.widgets.find(w => 
                        w.name === "display_text" || 
                        w.type === "text" || 
                        w.type === "customtext"
                    );
                    
                    // 方法2: 如果找不到，尝试第一个控件
                    if (!textWidget && this.widgets.length > 0) {
                        textWidget = this.widgets[0];
                        debug("使用第一个控件:", textWidget.name);
                    }
                    
                    // 更新文本显示
                    if (textWidget) {
                        debug(`更新控件 ${textWidget.name}`);
                        textWidget.value = textToDisplay;
                        app.graph.setDirtyCanvas(true);
                    } else {
                        debug("找不到可用的文本控件，尝试创建一个");
                        // 尝试创建控件
                        try {
                            this.addWidget("text", "display_text", textToDisplay, function(){}, { 
                                multiline: true,
                                readOnly: true
                            });
                            app.graph.setDirtyCanvas(true);
                            debug("已创建新的文本控件");
                        } catch (e) {
                            debug("创建控件失败:", e);
                        }
                    }
                } else {
                    debug("未找到可显示的文本");
                }
            };
        }
    }
}); 