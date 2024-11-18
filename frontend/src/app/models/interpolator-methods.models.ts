export const interpolatorMethods = [
    {
        name : "KNN",
        params : [
            { name : "k", type: "number"}
        ]
    },
    {
        name : "Kriging",
        params : [
            { name : "method", type: "text" },
            { name : "variogram_model", type : "text" },
            { name : "nlags", type : "number" },
            { name : "weight", type : "checkbox"}
        ]
    }
]