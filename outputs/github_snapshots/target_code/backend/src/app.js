const express = require('express');
const { quoteRouter } = require('./routes/quote.routes');

const app = express();

app.use(express.json());
app.use('/api/v1/quotes', quoteRouter);

module.exports = { app };
