const express = require('express');
const app = express(),
      port = process.env.PORT || 3080;

app.get('/', (req,res) => {
    res.send('App Works !!!');
});

app.get('/time', (req,res) => {
    res.send(new Date());
});

app.listen(port, () => {
    console.log(`Server listening on the port::${port}`);
});
