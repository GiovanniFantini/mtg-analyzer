'use strict';
// Reuses the existing audit without overwriting its historical output directory.
// Run from the repository root: node reviews/draft-bots-20261029/run-audit.cjs
const fs=require('node:fs'),path=require('node:path'),Module=require('node:module');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../..');
const original=fs.readFileSync(path.join(root,'audit-draft-bots.cjs'),'utf8');
const old="path.join(__dirname,'reviews','draft-bots-20261022')";
if(!original.includes(old))throw Error('Audit output contract changed; inspect before running.');
const source=original.replace(old,"path.join(__dirname,'reviews','draft-bots-20261029')");
if(process.argv[2]==='--worker'){
 const [slug,scenario,tables]=process.argv.slice(3);
 process.argv=[process.execPath,path.join(root,'audit-draft-bots.cjs'),tables,slug,'draft',scenario,'3'];
 const mod=new Module(process.argv[1],module);mod.filename=process.argv[1];mod.paths=Module._nodeModulePaths(root);
 mod._compile(source,mod.filename);
}else{
 const jobs=[['reality-fracture','mixed',80],['reality-fracture','power',20]];
 for(const [slug,scenario,tables] of jobs){
  const result=spawnSync(process.execPath,[__filename,'--worker',slug,scenario,String(tables)],{cwd:root,encoding:'utf8',maxBuffer:16*1024*1024});
  if(result.status!==0)throw Error(result.stderr||result.stdout);
  const report=JSON.parse(fs.readFileSync(path.join(__dirname,`${slug}-draft-${scenario}-v3.json`),'utf8'));
  console.log(JSON.stringify({slug,scenario,tables,botPicks:report.botPicks,byStrategy:report.byStrategy,flags:report.suspiciousExamples.length}));
 }
}
