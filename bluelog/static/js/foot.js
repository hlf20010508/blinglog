let date = new Date()
let year = date.getFullYear()
let element = document.getElementsByClassName('year')[0]
element.textContent = year
let host = location.protocol + '//' + document.domain + ':' + location.port
if (host != 'http://124.223.224.49:5000') {
    element = document.getElementsByClassName('indexLink')[0]
    element.setAttribute('target', '_blank')
}