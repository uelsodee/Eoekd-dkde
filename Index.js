const { Client, GatewayIntentBits } = require('discord.js');
require('dotenv').config();  // Utilisation de dotenv pour gérer les variables d'environnement

// Création du client Discord
const client = new Client({ 
    intents: [
        GatewayIntentBits.Guilds, 
        GatewayIntentBits.GuildMessages, 
        GatewayIntentBits.MessageContent
    ]
});

// Quand le bot est prêt
client.once('ready', () => {
    console.log(`Connecté en tant que ${client.user.tag}`);
});

// Si un message est envoyé avec le contenu '+ping'
client.on('messageCreate', message => {
    if (message.content === '+ping') {
        message.reply('Pong !');
    }
});

// Connexion au bot avec la variable d'environnement
client.login(process.env.DISCORD_TOKEN);  // Utilisation de la variable DISCORD_TOKEN
