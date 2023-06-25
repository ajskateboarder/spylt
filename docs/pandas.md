# DataFrame support

Spylt allows users to send dataframes from backend functions to be used on the frontend through [`dataframe-js`](https://github.com/Gmousse/dataframe-js).

## Usage

Simply add a `DataFrame` return type hint to a backend function, and make sure that your function returns a DataFrame object (not JSON, CSV, etc.)

You can reference this type however you want, as long as the underlying type is a `pandas.core.frame.DataFrame`

```py
@app.backend()
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

## Specifying a shape (TODO)

You can improve wrapper type hinting on the frontend by specifying the exact columns that you return from a DataFrame in a backend function.

You can add this functionality by passing the columns you return in the `@app.backend` decorator.

```py
@app.backend("First Name", "Last Name")
def get_names() -> pd.DataFrame:
    """
    Return the first and last names of all employees
    """
    return pd.read_csv("./data/employees.csv")[["First Name", "Last Name"]]
```

This way, the JavaScript wrapper can use this information to generate child classes which access those specific columns:

```js
class Employee extends DataFrame {
  constructor() {
    super();
  }
  /** @returns {DataFrame} */
  firstName() {
    return super().select("First Name");
  }
  /** @returns {DataFrame} */
  lastName() {
    return super().select("Last Name");
  }
}
```

These are also used as return types for functions which specify columns.
