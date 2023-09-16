const mongoose = require("mongoose")

const userSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true
    },
    username: {
        type: String,
        required: true
    },
    userMail: {
        type: String,
        required: true
    },
    userPassword: {
        type: String,
        required: true
    },
})

const user = mongoose.model("UserDB", userSchema)
module.exports = user