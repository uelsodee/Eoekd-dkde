const { Client, GatewayIntentBits } = require('discord.js');
require('dotenv').config(); // Assure-toi que dotenv est installé !

const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages] });

client.once('ready', () => {
    console.log(`Connecté en tant que ${client.user.tag}`);
});

client.on('messageCreate', message => {
    if (message.content === '+ping') {
        message.reply('Pong !');
    }
});

// Se connecter au bot avec le token de l'environnement
client.login(process.env.TOKEN);
