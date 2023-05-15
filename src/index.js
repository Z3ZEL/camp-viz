const config = require('dotenv').config().parsed;
const fs = require('fs');

console.log("Hello "+config.GARMIN_EMAIL); 

console.log("Status : "+config.STATUS);

const { GarminConnect } = require('garmin-connect');
// Create a new Garmin Connect Client
// Uses credentials from garmin.config.json or uses supplied params




async function main(){
    const client = new GarminConnect({});

    //CHECK IF COOKIE FILE EXISTS
    if (fs.existsSync('cookie.json')) {
        //file exists
        const cookie = JSON.parse(fs.readFileSync('cookie.json', 'utf8'));
        await client.restore(cookie)
    }else{
        await client.login(config.GARMIN_EMAIL, config.GARMIN_PASSWORD);
        //SAVE COOKIE TO FILE
        const cookie = client.sessionJson;
        fs.writeFileSync('cookie.json', JSON.stringify(cookie));
    }

    const userInfo = await client.getUserInfo();
    console.log(userInfo);

}

main();