<!-- point ./src/App.py:app -->
<script>
    let name
    let greeting = ""
    const sayHello = () => {
        try {
            fetch("/api/say_hello?name=Bob")
                .then(res => res.json())
                .then(res => greeting = JSON.stringify(res))
        } catch(err) {
            greeting = err
        }
    }
</script>
<main>
    <input type="text" bind:value={name}>
    <button on:click={sayHello}>Say hello</button>
    <p>{greeting}</p>
</main>
        