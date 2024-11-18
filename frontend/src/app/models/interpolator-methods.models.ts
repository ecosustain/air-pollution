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
            { name : "method", type : "text", options : ['ordinary', 'universal'] },
            { name : "variogram_model", type : "text", options : ['linear', 'power', 'gaussian', 'spherical'] },
            { name : "nlags", type : "number" },
            { name : "weight", type : "checkbox"}
        ]
    }
]