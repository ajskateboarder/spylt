<!-- point App.py:app -->
<script>
    export let text
    import Box from './Box.svelte'
    setTimeout(() => text = "Hello world!", 5000)
</script>
<main>
    <Box></Box>
    <p>{text}</p>
</main>
