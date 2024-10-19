<script>
    // 检查 localStorage 中是否有会话ID
    let userId = localStorage.getItem('user_id');

    if (!userId) {
    // 如果没有，则生成一个新的会话ID
    userId = Math.random().toString(36).substr(2, 16);
    localStorage.setItem('user_id', userId);
}

    // 在提交时将 userId 作为参数传递
    function submitChat() {
    const inputText = document.querySelector("input[type='text']").value;

    // 发起请求时，将用户ID传递给后端
    gradioApp().submit({input_text: inputText, user_id: userId});
}

    // 按钮点击事件绑定
    document.querySelector("button[type='submit']").addEventListener("click", submitChat);
</script>
