export const interpolatorMethods = [
    {
        name : "KNN",
        params : [
            { name : "k", type: "number"}
        ]
    },
    {
        name : "Krigin",
        params : [
            { name : "method", type: "text" },
            { name : "variogram_model", type : "text" },
            { name : "n_lags", type : "number" },
            { name : "weight", type : "checkbox"}
        ]
    }
]