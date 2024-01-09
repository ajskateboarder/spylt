# DataFrame support

Spylt allows users to send dataframes from backend functions to be used on the frontend through [`dataframe-js`](https://github.com/Gmousse/dataframe-js).

## Usage

Simply add a `DataFrame` return type hint to a backend function, and make sure that your function returns a DataFrame object (not JSON, CSV, etc.)

You can reference this type however you want, as long as the underlying type is a `pandas.core.frame.DataFrame`

```py
@app.f
def get_names() -> pd.DataFrame:
    """Return the first and last names of all employees"""
    return pd.read_csv("./data/employees.csv")[["First Name", "Last Name"]]
```

When you call `spylt interface` in your project, you should have wrapper code like the following:

```js
/**
 * Return the first and last names of all employees
 * @returns {DataFrame}
 */
export function get_names() {
    const res = fetchSync(`/api/get_names?`);
    return DataFrame(res.response);
}
```