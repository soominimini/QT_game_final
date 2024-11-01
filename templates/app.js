/* draggable element */

let item = document.querySelectorAll('.item');

let score =0;
let currentId = "";
let currentImg = "";

item.forEach(e => {
  e.addEventListener('dragstart', dragStart);
})
function dragStart(e) {
    console.log("e.target: ",e.target);
    current_data_id =e.target.getAttribute("data-source-id");
    currentId = e.target.getAttribute("id");
    e.dataTransfer.setData('text/plain', e.target.id);

}


/* drop targets */
// const boxes = document.querySelectorAll('.box');
const cart = document.querySelectorAll('.cart');

cart.forEach(box => {
    box.addEventListener('dragenter', dragEnter)
    box.addEventListener('dragover', dragOver);
    box.addEventListener('dragleave', dragLeave);
    box.addEventListener('drop', drop);
});


function dragEnter(e) {
    e.preventDefault();
    e.target.classList.add('drag-over');
}

function dragOver(e) {
    e.preventDefault();
    e.target.classList.add('drag-over');
}

function dragLeave(e) {
    e.target.classList.remove('drag-over');
}

function drop(drop_e) {


    // const dataSourceId = e.target.getAttribute('data-target-id');
    const dataTargetId = drop_e.target.getAttribute('data-target-id');

    if(current_data_id==dataTargetId){
        drop_e.target.classList.remove('drag-over');

        // get the draggable element
        const id = drop_e.dataTransfer.getData('text/plain');
        const draggable = document.getElementById(id);

        // add it to the drop target
        // e.target.appendChild(draggable);

        // display the draggable element
        // draggable.classList.remove('hide');
        console.log("score+1");
        score+=1;
        console.log(currentId);
        // e.target.classList.add('hide');
        console.log(document.getElementById(currentId));
        document.getElementById(currentId).classList.add('hide');


        // tagArea.appendChild(new_hTag);
    }
    else{
        console.log("wrong answer");
        score-=1;
    }

}