const easyMDE = new EasyMDE({
    element: document.getElementById("body"),
    unorderedListStyle: '-',
    previewImagesInEditor: true,
    insertTexts: {
        horizontalRule: ["", "\n\n-----\n\n"],
        image: ["![](", ")"],
        link: ["[", "]()"],
        table: ["", "\n\n| Column 1 | Column 2 | Column 3 |\n| -------- | -------- | -------- |\n| Text     | Text      | Text     |\n\n"],
    },
    uploadImage: true,
    imageMaxSize: 50 * 1024 * 1024,
    imageAccept: "image/png, image/jpeg, image/jpg, image/gif",
    imageUploadFunction: (file, onSuccess, onError) => {
        let form = new FormData
        form.append('file', file)
        axios({
            method: 'post',
            url: '/admin/upload',
            data: form,
            headers: {
                "X-CSRFToken": document.getElementById('csrf_token').getAttribute('value')
            }
        }).then((res) => {
            if (res.data.success) {
                onSuccess(res.data.url)
            }
            else {
                onError(res.data.error)
            }
        })
    },
    toolbar: [
        'bold',
        'italic',
        'strikethrough',
        'heading',
        "|",
        'quote',
        'code',
        'unordered-list',
        'ordered-list',
        'clean-block',
        "|",
        'link',
        'upload-image',
        'table',
        'horizontal-rule',
        "|",
        'preview',
        'side-by-side',
        'fullscreen',

    ]
});