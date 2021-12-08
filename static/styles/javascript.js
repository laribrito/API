//para apagar a mensagem depois de 5 segundos
setTimeout(function(){
    var el = document.getElementById("mensagem");
    el.style.display="None";
},5000);

//essa função encaminha para o perfil
function paraPerfil(login){
    window.location.href="/perfil/"+login;
    console.log(login);
};

//PARA CURTIR E DESCURTIR
function queroCurtir(id){
    //esconde o botão que foi apertado
    var idC = "curtir"+id;
    var el = document.getElementById(idC);
    el.style.display = "None";
  
    //exibe o outro
    var idDC = "deixarCurtir"+id;
    el = document.getElementById(idDC);
    el.style.display = "inline";
  
    //Aumenta a contagem do labelCurtidas
    var idLC = "labelCurtidas"+id;
    el = document.getElementById(idLC);
    //pega o conteudo do <p>
    var num = el.innerText;
    //transforma em inteiro
    num = parseInt(num, 10);
    //incrementa
    num += 1;
    //exibe o novo número
    el.innerHTML = num;
};
function queroDeixarCurtir(id){
//esconde o botão que foi apertado
var idDC = "deixarCurtir"+id;
var el = document.getElementById(idDC);
el.style.display = "None"

//exibe o outro
var idC = "curtir"+id;
var el = document.getElementById(idC);
el.style.display = "inline";

//Diminue a contagem do labelCurtidas
var idLC = "labelCurtidas"+id;
el = document.getElementById(idLC);
//pega o conteudo do <p>
var num = el.innerText;
//transforma em inteiro
num = parseInt(num, 10);
//decrementa
num -= 1;
//exibe o novo número
el.innerHTML = num;
};
