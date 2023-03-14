<!-- point ./src/App.py:app -->
<script>
    let greeting
    let name = "Bob"
    const sayHello = () => {
        fetch(`/api/say_hello?name=${name}`)
            .then(res => res.json())
            .then(res => greeting = JSON.stringify(res))
    }
</script>
<main>
    <input type="text" bind:value={name}>
    <button on:click={sayHello}>Say hello</button>
    <p>{greeting}</p>
</main>
        