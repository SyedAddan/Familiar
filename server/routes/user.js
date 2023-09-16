const express = require('express')

const userController = require('../controllers/user')

const router = express.Router()

router.get("/getUsers", userController.getUsers)

module.exports = router