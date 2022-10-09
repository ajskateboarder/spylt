<script>
    export let text;
    setTimeout(() => (text = "Hello world!"), 5000);
</script>

<p class="content">{text}</p>

<style>
    .content {
        font-family: Arial, Helvetica, sans-serif;
        font-size: 30px;
    }
</style>
