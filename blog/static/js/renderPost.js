// 在服务器直接渲染会造成与预览时不一致的问题
// 为保证与预览的渲染结果一致，直接在前端调用编辑器进行渲染

let contentDiv = document.getElementById("raw-content")
let contentDivHidden = document.getElementById("raw-content-hidden")
let rawContent = contentDivHidden.textContent
let htmlContent = easyMDE.markdown(rawContent)
contentDiv.innerHTML = htmlContent