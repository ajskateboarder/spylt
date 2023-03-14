export const say_hello = async (name) => { 
    request = await fetch(`/api/say_hello?name=${name}`)
    json = await request.json()
    return json.response
}