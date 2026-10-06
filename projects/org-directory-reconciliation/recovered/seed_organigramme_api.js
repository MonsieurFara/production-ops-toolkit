// Version publique adaptée ; voir docs/recovered-scripts.md.



const fs = require("fs");
const path = require("path");


const REGLES_POSTE = [
    { motif: /DIRECTEUR\s+GENERAL\s+ADJOINT/, grade: "Directeur Général", fonction: "Directeur General Adjoint", niveau: 1 },
    { motif: /DIRECTEUR\s+GENERAL/, grade: "Directeur Général", fonction: "Directeur Général", niveau: 1 },
    { motif: /DIRECTEUR\s+ADJOINT/, grade: "Directeur", fonction: "Directeur Adjoint", niveau: 1 },
    { motif: /SOUS[-\s]?DIRECTEUR/, grade: "Directeur", fonction: "Sous-Directeur", niveau: 1 },
    { motif: /DIRECTEUR/, grade: "Directeur", fonction: "Directeur", niveau: 1 },
    { motif: /CHEF\s+DE\s+DEPARTEMENT/, grade: "Chef de Département", fonction: "Chef de Département", niveau: 1 },
    { motif: /CHEF\s+(DE\s+)?SERVICE\s+PRINCIPAL/, grade: "Chef Service Principal", fonction: null, niveau: 1 },
    { motif: /CHEF\s+DE\s+SERVICE/, grade: "Chef de Service", fonction: null, niveau: 1 },
    { motif: /CHEF\s+DE\s+PROJET/, grade: "Chef de Projet", fonction: null, niveau: 2 },



    { motif: /CHEF\s+D.?UNITE\s+(CENTRALE|DECENTRALISEE).*COORDO/, grade: "Chef de Département", fonction: "Directeur", niveau: 1 },
    { motif: /CHEF\s+D.?UNITE\s+CENTRALE/, grade: "Chef de Service", fonction: "Directeur", niveau: 1 },
    { motif: /CHEF\s+D.?UNITE\s+DECENTRALISEE/, grade: "DA", fonction: "DA", niveau: 1 },
    { motif: /CHEF\s+DE\s+S\/?.?UNITE/, grade: "Chef de Service", fonction: null, niveau: 2 },

    { motif: /INGENIEUR\s+DEVELOPPEUR/, grade: "Analyste", fonction: "Ingenieur Developpeur", niveau: 3 },
    { motif: /INGENIEUR/, grade: "Analyste", fonction: "Ingenieur Developpeur", niveau: 3 },
    { motif: /ANALYSTE/, grade: "Analyste", fonction: "Analyste", niveau: 3 },
    { motif: /ARCHIVISTE/, grade: "Archiviste", fonction: "Archiviste", niveau: 3 },
    { motif: /AGI/, grade: "AGI", fonction: "AGI", niveau: 3 },
    { motif: /GFC|GESTIONNAIRE/, grade: "Gestionnaire", fonction: "Gestionnaire", niveau: 3 },
];


function lireArguments(argv) {
    const opts = { execute: false, skipUnites: false, skipEmployes: false, limit: null };
    for (let i = 2; i < argv.length; i++) {
        const a = argv[i];
        const suivant = () => argv[++i];
        if (a === "--url") opts.url = suivant();
        else if (a === "--user") opts.user = suivant();
        else if (a === "--password") throw new Error("Utiliser ORG_API_PASSWORD, hors ligne de commande");
        else if (a === "--seed") opts.seed = suivant();
        else if (a === "--filiale") opts.filiale = suivant();
        else if (a === "--limit") opts.limit = parseInt(suivant(), 10);
        else if (a === "--execute") opts.execute = true;
        else if (a === "--skip-unites") opts.skipUnites = true;
        else if (a === "--skip-employes") opts.skipEmployes = true;
        else if (a === "--reset-unites") opts.resetUnites = true;
        else if (a === "--skip-referentiels") opts.skipReferentiels = true;
        else if (a === "--aucune-creation") opts.aucuneCreation = true;
        else if (a === "--help" || a === "-h") opts.help = true;
    }
    opts.url = (opts.url || process.env.ORG_API_URL || "").replace(/\/+$/, "");
    opts.user = opts.user || process.env.ORG_API_USER;
    opts.password = opts.password || process.env.ORG_API_PASSWORD;
    opts.seed = opts.seed || path.join(__dirname, "organigramme_seed.json");
    return opts;
}

const OPT = lireArguments(process.argv);

if (OPT.help || !OPT.url || !OPT.user || !OPT.password) {
    console.log(`
Chargement de l'organigramme via l'API REST.

  node seed_organigramme_api.js --url <api> --user <login>  [--execute]

  --url        URL de l'API, ex. http://organigramme-api.example.com
  --user       Identifiant (l'email fonctionne)
  ORG_API_PASSWORD : variable de processus protégée
  --seed       Fichier de seed (defaut: ./organigramme_seed.json)
  --filiale    Filiale ciblee (id ou libelle ; defaut: l'unique filiale)
  --execute    Ecrit reellement. SANS cette option, simple simulation.
  --limit <n>  Limite le nombre d'employes traites (test)
  --skip-unites / --skip-employes
  --reset-unites  Supprime l'arborescence existante avant de la recreer.
                  Evite les doublons quand les unites en base portent des
                  libelles differents de ceux de l'export RH.
                  Ne supprime QUE des unites, jamais des employes.

Sans --execute, le script n'ecrit RIEN : il affiche ce qui serait fait.
Certaines options peuvent supprimer des unites ; consulter la documentation.
`);
    process.exit(OPT.help ? 0 : 1);
}


const endpointPublicCheck = new URL(OPT.url);
if (endpointPublicCheck.username || endpointPublicCheck.password) throw new Error("Identifiants interdits dans l'URL");
if (endpointPublicCheck.protocol !== "https:" && !(endpointPublicCheck.protocol === "http:" && ["localhost", "127.0.0.1", "[::1]"].includes(endpointPublicCheck.hostname))) throw new Error("HTTPS requis hors localhost");

const DRY_RUN = !OPT.execute;


let TOKEN = null;


async function appel(methode, chemin, corps) {
    const entetes = { Accept: "application/json" };
    if (TOKEN) entetes.Authorization = `Bearer ${TOKEN}`;
    if (corps) entetes["Content-Type"] = "application/json";
    try {
        const reponse = await fetch(`${OPT.url}${chemin}`, {
            method: methode,
            signal: AbortSignal.timeout(10000),
            headers: entetes,
            body: corps ? JSON.stringify(corps) : undefined,
        });
        const texte = await reponse.text();
        let json = null;
        try { json = texte ? JSON.parse(texte) : null; } catch {  }
        return {
            ok: reponse.ok && (json === null || json.success !== false),
            status: reponse.status,
            data: json && json.data !== undefined ? json.data : json,
            message: (json && json.message) || texte.slice(0, 200),
        };
    } catch (e) {
        return { ok: false, status: 0, data: null, message: e.message };
    }
}

const GET = (c) => appel("GET", c);
const POST = (c, b) => appel("POST", c, b);
const PUT = (c, b) => appel("PUT", c, b);

const pause = (ms) => new Promise((r) => setTimeout(r, ms));


async function connexion(tentatives = 4) {
    for (let essai = 1; essai <= tentatives; essai++) {
        const r = await POST("/api/auth/login", { username: OPT.user, password: OPT.password });
        const jeton = r.data && (r.data.access_token || r.data.accessToken || r.data.token);
        if (r.ok && jeton) { TOKEN = jeton; return; }

        if (essai === tentatives) {
            throw new Error(`Authentification refusee apres ${tentatives} tentatives : ${r.message}`);
        }
        const attente = essai * 20;
        console.log(`  authentification refusee (${r.message}) - nouvelle tentative dans ${attente}s...`);
        await pause(attente * 1000);
    }
}


const normaliser = (s) => (s || "").toString().normalize("NFD")
    .replace(/[̀-ͯ]/g, "").toUpperCase().trim();


function trouverParLibelle(liste, libelle, champs) {
    if (!libelle) return null;
    const cible = normaliser(libelle);
    return liste.find((el) => champs.some((c) => normaliser(el[c]) === cible)) || null;
}


function classerPoste(libelle) {
    const texte = normaliser(libelle);
    for (const regle of REGLES_POSTE) {
        if (regle.motif.test(texte)) return regle;
    }
    return null;
}

function barre(titre) {
    console.log("");
    console.log("=".repeat(72));
    console.log(titre);
    console.log("=".repeat(72));
}


async function main() {
    barre(`CHARGEMENT ORGANIGRAMME  -  ${DRY_RUN ? "SIMULATION (aucune ecriture)" : "EXECUTION REELLE"}`);
    console.log(`API   : ${OPT.url}`);
    console.log(`Seed  : ${OPT.seed}`);


    if (!fs.existsSync(OPT.seed)) throw new Error(`Fichier de seed introuvable : ${OPT.seed}`);
    const seed = JSON.parse(fs.readFileSync(OPT.seed, "utf8"));
    console.log(`Source: ${seed.source} (genere le ${seed.genereLe})`);
    console.log(`A charger : ${seed.unites.length} unites, ${seed.employes.length} employes`);

    await connexion();
    console.log("Authentification : OK");


    const filiales = (await GET("/api/filiales")).data || [];
    let filiale;
    if (OPT.filiale) {
        filiale = filiales.find((f) => f.id === OPT.filiale)
            || trouverParLibelle(filiales, OPT.filiale, ["libFiliale"]);
    } else if (filiales.length === 1) {
        filiale = filiales[0];
    }
    if (!filiale) {
        console.error("Filiale non determinee. Preciser --filiale parmi :");
        filiales.forEach((f) => console.error(`   ${f.id}  ${f.libFiliale}`));
        process.exit(1);
    }
    console.log(`Filiale : ${filiale.libFiliale} (${filiale.id})`);


    const typesUnite = (await GET("/api/types-unite")).data || [];
    let grades = (await GET("/api/grades-employe")).data || [];
    let fonctions = (await GET("/api/fonctions")).data || [];



    const champsType = ["libUnite", "codeTypeUnite", "libTypeUnite", "libelle", "code"];
    const typeAgence = trouverParLibelle(typesUnite, "Agence", champsType);
    const typeDirection = trouverParLibelle(typesUnite, "Direction", champsType);
    const TYPE_PAR_NATURE = {
        AGENCE: typeAgence && typeAgence.id,
        RESEAU: (typeDirection && typeDirection.id) || (typeAgence && typeAgence.id),
        UNITE: (typeDirection && typeDirection.id) || (typeAgence && typeAgence.id),
    };
    console.log(`Referentiels : ${typesUnite.length} types, ${grades.length} grades, ${fonctions.length} fonctions`);
    if (!typeAgence) console.log("  ! type d'unite 'Agence' introuvable (idTypeUnite laisse vide)");
    if (!typeDirection) console.log("  ! type d'unite 'Direction' introuvable");


    const unitesExistantes = (await GET(`/api/unites?idFiliale=${filiale.id}`)).data || [];
    const employesExistants = (await GET("/api/employes")).data || [];
    console.log(`Etat actuel  : ${unitesExistantes.length} unites, ${employesExistants.length} employes`);

    if (!DRY_RUN) {
        const nomEnv = OPT.url.replace(/^https?:\/\//, "").replace(/[^a-z0-9]+/gi, "-");



        const horodatage = new Date().toISOString().slice(0, 16).replace(/[-:]/g, "").replace("T", "-");
        const fichierBackup = path.join(__dirname, `backup_${nomEnv}_${horodatage}.json`);
        fs.writeFileSync(fichierBackup, JSON.stringify(
            { date: new Date().toISOString(), api: OPT.url, filiale, unites: unitesExistantes, employes: employesExistants },
            null, 2), "utf8");
        console.log(`Sauvegarde   : ${fichierBackup}`);
    }
















    const erreursReset = [];
    let unitesAvant = unitesExistantes;
    if (OPT.resetUnites) {
        barre("REMISE A ZERO DE L'ARBORESCENCE");
        const parId = new Map(unitesExistantes.map((u) => [u.id, u]));
        const profondeur = (u) => {
            let n = 1, courant = u, garde = 0;
            while (courant && courant.superieurId && garde++ < 20) { courant = parId.get(courant.superieurId); n++; }
            return n;
        };
        const aSupprimer = [...unitesExistantes].sort((a, b) => profondeur(b) - profondeur(a));
        console.log(`  ${aSupprimer.length} unites a supprimer (des plus profondes vers la racine)`);

        if (DRY_RUN) {
            console.log("  [SIMULATION] aucune suppression effectuee.");
        } else {
            let supprimees = 0, echecs = 0;
            for (const u of aSupprimer) {
                const r = await appel("DELETE", `/api/unites/${u.id}`);
                if (r.ok) supprimees++;
                else { echecs++; erreursReset.push(`SUPPRESSION ${u.libUnite} [${u.code || "-"}] (${r.status}) ${r.message}`); }
            }
            console.log(`  supprimees : ${supprimees}   echecs : ${echecs}`);
            unitesAvant = (await GET(`/api/unites?idFiliale=${filiale.id}`)).data || [];
            console.log(`  unites restantes : ${unitesAvant.length}`);
        }
    }



    const uniteParCode = new Map();
    const uniteParLibelle = new Map();
    (OPT.resetUnites && !DRY_RUN ? unitesAvant : (OPT.resetUnites ? [] : unitesExistantes)).forEach((u) => {
        if (u.code) uniteParCode.set(normaliser(u.code), u);
        if (u.libUnite) uniteParLibelle.set(normaliser(u.libUnite), u);
    });

    const idParCodeSeed = new Map();   
    const stats = {
        referentiels: { fonctionsCreees: 0, gradesCrees: 0, erreurs: 0 },
        unites: { creees: 0, majs: 0, erreurs: 0 },
        liens: { poses: 0, erreurs: 0 },
        employes: { crees: 0, majs: 0, ignores: 0, sansEmail: 0, nonTrouves: 0, erreurs: 0 },
    };
    const erreurs = [...erreursReset];
    const postesNonMappes = new Map();














    const libellesPostes = [...new Set(
        seed.employes.map((e) => e.fonctionLibelle).filter(Boolean).map((l) => l.trim())
    )].sort();

    if (!OPT.skipReferentiels) {
        barre("PHASE 1/4  -  REFERENTIELS (fonctions et grades)");
        console.log(`  ${libellesPostes.length} libelles distincts dans l'export RH`);

        const codesPris = new Set([
            ...fonctions.map((f) => normaliser(f.codeFct)),
            ...grades.map((g) => normaliser(g.codeGrade)),
        ]);

        function genererCode(libelle) {
            let base = normaliser(libelle).replace(/[^A-Z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 24);
            if (!base) base = "POSTE";
            let code = base, n = 2;
            while (codesPris.has(normaliser(code))) code = `${base.slice(0, 21)}-${n++}`;
            codesPris.add(normaliser(code));
            return code;
        }

        for (const libelle of libellesPostes) {
            if (!trouverParLibelle(fonctions, libelle, ["libFct", "libelle"])) {
                if (DRY_RUN) {


                    fonctions.push({ id: `SIMULE-FCT-${libelle}`, libFct: libelle });
                    stats.referentiels.fonctionsCreees++;
                } else {
                    const r = await POST("/api/fonctions", { codeFct: genererCode(libelle), libFct: libelle, rang: 99 });
                    if (r.ok && r.data) { fonctions.push(r.data); stats.referentiels.fonctionsCreees++; }
                    else { stats.referentiels.erreurs++; erreurs.push(`FONCTION "${libelle}" (${r.status}) ${r.message}`); }
                }
            }
            if (!trouverParLibelle(grades, libelle, ["libGrade", "libelle"])) {
                if (DRY_RUN) {
                    grades.push({ id: `SIMULE-GRD-${libelle}`, libGrade: libelle });
                    stats.referentiels.gradesCrees++;
                } else {
                    const r = await POST("/api/grades-employe", { codeGrade: genererCode(libelle), libGrade: libelle, rang: 99 });
                    if (r.ok && r.data) { grades.push(r.data); stats.referentiels.gradesCrees++; }
                    else { stats.referentiels.erreurs++; erreurs.push(`GRADE "${libelle}" (${r.status}) ${r.message}`); }
                }
            }
        }
        console.log(`  fonctions creees : ${stats.referentiels.fonctionsCreees}   grades crees : ${stats.referentiels.gradesCrees}   erreurs : ${stats.referentiels.erreurs}`);
    }




    if (!OPT.skipUnites) {
        barre("PHASE 2/4  -  UNITES");
        for (const u of seed.unites) {
            const existante = uniteParCode.get(normaliser(u.code)) || uniteParLibelle.get(normaliser(u.libUnite));
            const corps = {
                idFiliale: filiale.id,
                idTypeUnite: TYPE_PAR_NATURE[u.nature] || null,
                code: u.code,
                libUnite: u.libUnite,
            };

            if (existante) {
                idParCodeSeed.set(u.code, existante.id);
                if (DRY_RUN) { stats.unites.majs++; continue; }
                const r = await PUT(`/api/unites/${existante.id}`, { ...existante, ...corps });
                if (r.ok) stats.unites.majs++;
                else { stats.unites.erreurs++; erreurs.push(`UNITE MAJ ${u.code} (${r.status}) ${r.message}`); }
            } else {
                if (DRY_RUN) { idParCodeSeed.set(u.code, `SIMULE-${u.code}`); stats.unites.creees++; continue; }
                const r = await POST("/api/unites", corps);
                if (r.ok && r.data && r.data.id) {
                    idParCodeSeed.set(u.code, r.data.id);
                    stats.unites.creees++;
                } else {
                    stats.unites.erreurs++;
                    erreurs.push(`UNITE CREATION ${u.code} (${r.status}) ${r.message}`);
                }
            }
        }
        console.log(`  creees : ${stats.unites.creees}   mises a jour : ${stats.unites.majs}   erreurs : ${stats.unites.erreurs}`);






        barre("PHASE 3/4  -  HIERARCHIE DES UNITES");
        for (const u of seed.unites) {
            const idEnfant = idParCodeSeed.get(u.code);




            if (!u.parentCode) {
                if (!idEnfant || DRY_RUN) { stats.liens.poses++; continue; }
                const courante = (await GET(`/api/unites/${idEnfant}`)).data;
                if (courante && courante.superieurId) {
                    const r = await PUT(`/api/unites/${idEnfant}`, { ...courante, superieurId: null });
                    if (r.ok) stats.liens.poses++;
                    else { stats.liens.erreurs++; erreurs.push(`RACINE ${u.code} (${r.status}) ${r.message}`); }
                }
                continue;
            }

            const idParent = idParCodeSeed.get(u.parentCode);
            if (!idEnfant || !idParent) {
                stats.liens.erreurs++;
                erreurs.push(`LIEN ${u.code} -> ${u.parentCode} : unite absente`);
                continue;
            }
            if (DRY_RUN) { stats.liens.poses++; continue; }
            const actuelle = (await GET(`/api/unites/${idEnfant}`)).data;
            const r = await PUT(`/api/unites/${idEnfant}`, { ...actuelle, superieurId: idParent });
            if (r.ok) stats.liens.poses++;
            else { stats.liens.erreurs++; erreurs.push(`LIEN ${u.code} (${r.status}) ${r.message}`); }
        }
        console.log(`  liens poses : ${stats.liens.poses}   erreurs : ${stats.liens.erreurs}`);
    }





    if (!OPT.skipEmployes) {
        barre("PHASE 4/4  -  EMPLOYES");

        const employeParEmail = new Map();
        employesExistants.forEach((e) => {
            if (e.adresseEmail) employeParEmail.set(e.adresseEmail.toLowerCase(), e);
        });











        const cleNomMatricule = (nom, mat) => `${normaliser(nom)}|${String(mat).trim()}`;
        const employeParNomMatricule = new Map();
        employesExistants.forEach((e) => {
            if (e.matEmploye && e.nomEmploye) employeParNomMatricule.set(cleNomMatricule(e.nomEmploye, e.matEmploye), e);
        });




        const occurrences = new Map();
        employesExistants.forEach((e) => {
            if (!e.matEmploye) return;
            const cle = String(e.matEmploye).trim();
            occurrences.set(cle, (occurrences.get(cle) || 0) + 1);
        });
        const employeParMatricule = new Map();
        employesExistants.forEach((e) => {
            if (!e.matEmploye) return;
            const cle = String(e.matEmploye).trim();
            if (occurrences.get(cle) === 1) employeParMatricule.set(cle, e);
        });

        const nonTrouves = [];
        const emailsTraites = new Set();
        let liste = seed.employes;
        if (OPT.limit) liste = liste.slice(0, OPT.limit);

        let compteur = 0;
        for (const emp of liste) {
            compteur++;
            if (compteur % 200 === 0) console.log(`  ... ${compteur}/${liste.length}`);

            const email = emp.adresseEmail ? emp.adresseEmail.toLowerCase() : null;






            let emailRetenu = emp.adresseEmail || null;
            if (email && emailsTraites.has(email)) {
                emailRetenu = null;
                stats.employes.sansEmail++;
                erreurs.push(`EMAIL DEJA ATTRIBUE, charge sans email : ${emp.nomEmploye} (mat ${emp.matricule}) / ${email}`);
            } else if (email) {
                emailsTraites.add(email);
            }




            const fonction = trouverParLibelle(fonctions, emp.fonctionLibelle, ["libFct", "libelle"]);
            const grade = trouverParLibelle(grades, emp.fonctionLibelle, ["libGrade", "libelle"]);
            if (emp.fonctionLibelle && (!fonction || !grade)) {
                postesNonMappes.set(emp.fonctionLibelle, (postesNonMappes.get(emp.fonctionLibelle) || 0) + 1);
            }



            const poste = classerPoste(emp.fonctionLibelle);

            const idUnite = emp.uniteCode ? idParCodeSeed.get(emp.uniteCode) : null;
            const idUniteReel = idUnite && !String(idUnite).startsWith("SIMULE-") ? idUnite : null;









            const champsMetier = {
                idFiliale: filiale.id,
                idUnite: idUniteReel,
                matEmploye: emp.matricule || null,
                idGrade: grade ? grade.id : null,
                idFonction: fonction ? fonction.id : null,
                niveau: poste ? poste.niveau : null,
            };






            let existant = emailRetenu ? employeParEmail.get(emailRetenu.toLowerCase()) : null;
            if (!existant && emp.matricule && emp.nomEmploye) {
                existant = employeParNomMatricule.get(cleNomMatricule(emp.nomEmploye, emp.matricule));
            }





            if (!existant && emp.matricule) {
                existant = employeParMatricule.get(String(emp.matricule).trim());
            }

            if (existant) {
                if (DRY_RUN) { stats.employes.majs++; continue; }



                const r = await PUT(`/api/employes/${existant.id}`, { ...existant, ...champsMetier });
                if (r.ok) stats.employes.majs++;
                else { stats.employes.erreurs++; erreurs.push(`EMPLOYE MAJ ${emp.nomEmploye} (${r.status}) ${r.message}`); }
            } else if (OPT.aucuneCreation) {





                stats.employes.nonTrouves++;
                nonTrouves.push(`${emp.nomEmploye} (mat ${emp.matricule || "-"}) / ${emp.adresseEmail || "sans email"}`);
            } else {
                if (DRY_RUN) { stats.employes.crees++; continue; }
                const r = await POST("/api/employes", {
                    ...champsMetier,
                    nomEmploye: emp.nomEmploye,   
                    adresseEmail: emailRetenu,
                    username: emp.username || null,
                });
                if (r.ok) stats.employes.crees++;
                else { stats.employes.erreurs++; erreurs.push(`EMPLOYE CREATION ${emp.nomEmploye} (${r.status}) ${r.message}`); }
            }
        }
        console.log(`  crees : ${stats.employes.crees}   mis a jour : ${stats.employes.majs}   charges sans email : ${stats.employes.sansEmail}   non trouves : ${stats.employes.nonTrouves}   erreurs : ${stats.employes.erreurs}`);
        if (nonTrouves.length) {
            console.log(`
  --- ${nonTrouves.length} PERSONNES NON TROUVEES (non creees) ---`);
            nonTrouves.slice(0, 30).forEach((n) => console.log(`      ${n}`));
            if (nonTrouves.length > 30) console.log(`      ... et ${nonTrouves.length - 30} autres`);
            erreurs.push(...nonTrouves.map((n) => `NON TROUVE (non cree) : ${n}`));
        }
    }




    barre("RAPPORT");
    console.log(`Referentiels: ${stats.referentiels.fonctionsCreees} fonctions creees, ${stats.referentiels.gradesCrees} grades crees, ${stats.referentiels.erreurs} erreurs`);
    console.log(`Unites    : ${stats.unites.creees} creees, ${stats.unites.majs} mises a jour, ${stats.unites.erreurs} erreurs`);
    console.log(`Hierarchie: ${stats.liens.poses} liens poses, ${stats.liens.erreurs} erreurs`);
    console.log(`Employes  : ${stats.employes.crees} crees, ${stats.employes.majs} mis a jour, ${stats.employes.sansEmail} charges sans email, ${stats.employes.nonTrouves} non trouves, ${stats.employes.erreurs} erreurs`);
    console.log("Aucune suppression n'a ete effectuee.");

    if (postesNonMappes.size) {
        console.log(`\n--- LIBELLES DE POSTE NON MAPPES (${postesNonMappes.size}) ---`);
        console.log("  Grade et fonction laisses vides. Completer REGLES_POSTE en tete de script.");
        [...postesNonMappes.entries()].sort((a, b) => b[1] - a[1]).slice(0, 30)
            .forEach(([lib, n]) => console.log(`  ${String(n).padStart(4)}  ${lib}`));
        if (postesNonMappes.size > 30) console.log(`  ... et ${postesNonMappes.size - 30} autres`);
    }

    if (erreurs.length) {
        console.log(`\n--- ANOMALIES (${erreurs.length}) ---`);
        erreurs.slice(0, 40).forEach((e) => console.log(`  ${e}`));
        if (erreurs.length > 40) console.log(`  ... et ${erreurs.length - 40} autres`);
        const fichierErreurs = path.join(__dirname, "seed_anomalies.log");
        fs.writeFileSync(fichierErreurs, erreurs.join("\n"), "utf8");
        console.log(`  Journal complet : ${fichierErreurs}`);
    }

    barre(DRY_RUN
        ? "SIMULATION TERMINEE - aucune donnee modifiee.\nRelancer avec --execute pour appliquer."
        : "CHARGEMENT TERMINE.");
}

main().catch((e) => {
    console.error(`\nECHEC : ${e.message}`);
    process.exit(1);
});
