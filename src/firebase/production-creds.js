const FIREBASE_TOKEN = process.env.FIREBASE_TOKEN;
const FIREBASE_ID= "allen-cell-resource";
const FIREBASE_DB_URL = `https://${FIREBASE_ID}.firebaseapp.com`;
const FIREBASE_EMAIL= process.env.FIREBASE_EMAIL

  if (!FIREBASE_TOKEN) {
    console.error(
      "You need a secret token FIREBASE_TOKEN to use the production database"
    );
    process.exit(1);
  }
  if (!FIREBASE_EMAIL) {
    console.error(
      "You need a secret email FIREBASE_EMAIL to use the production database"
    );
    process.exit(1);
  }

module.exports = {
  FIREBASE_TOKEN,
  FIREBASE_ID,
  FIREBASE_DB_URL,
  FIREBASE_EMAIL,
};