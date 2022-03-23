$(function() {
	let operation = 'addItem';
	let selectedIndex = -1;
	let tableCurrentItems = [];
	let nameFileSave = 'lista_produtos.json';
	let arrayPropertyItemsJson = ['ProductID', 'ProductName', 'ProductJob', 'ProductProcess', 'ProductProcessSetup', 'ProductProcessTime', 'ProductProcessImpositions', 'ProductMaterial', 'ProductMaterialQuantity', 'ProductMaterialImpositions', 'ProductOutsourced', 'ProductOutsourcedTime', 'ProductOutsourcedImpositions', 'ProductProcessPredecessor', 'ProductProcessSuccessor'];
	let arrayValueItemsJson = ['#txtProductID', '#txtProductName', '#txtProductJob', '#txtProductProcess', '#txtProductProcessSetup', '#txtProductProcessTime', '#txtProductProcessImpositions', '#txtProductMaterial', '#txtProductMaterialQuantity', '#txtProductMaterialImpositions', '#txtProductOutsourced', '#txtProductOutsourcedTime', '#txtProductOutsourcedImpositions', '#txtProductProcessPredecessor', '#txtProductProcessSuccessor'];
	let arrayHeadTable = ['Job', 'ID', 'Produto', 'Processo', 'Setup', 'Tempo', 'Impos.', 'Mater.', 'Quant.', 'Impos', 'Terc.', 'Tempo', 'Impos', 'Predec', 'Suces'];
	let listItemsOfLocalStorage = 'tbProducts';
	
	let tbLocalJobs = localStorage.getItem('tbJobs');
	let tbLocalProcess = localStorage.getItem('tbProcess');
	let tbLocalMaterials = localStorage.getItem('tbMaterials');
	let tbLocalOutsourced = localStorage.getItem('tbOutsourced');
	
	tbLocalJobs = JSON.parse(tbLocalJobs);
	tbLocalProcess = JSON.parse(tbLocalProcess);
	tbLocalMaterials = JSON.parse(tbLocalMaterials);
	tbLocalOutsourced = JSON.parse(tbLocalOutsourced);

	tableCurrentItems = localStorage.getItem(listItemsOfLocalStorage);
	tableCurrentItems = JSON.parse(tableCurrentItems);

	if (tableCurrentItems == null) {
		tableCurrentItems = [];
	}

	function addItemToLocalStorage () {
		localStorage.setItem(listItemsOfLocalStorage, JSON.stringify(tableCurrentItems));
	}

	function addItemJson() {
		let item = getItemJson();

		if (item != null) {
			alert('ID já cadastrado.');
			return;
		}

		tableCurrentItems.push(itemObjectToJson());
		addItemToLocalStorage();
		return true;
	}

	function editItemJson() {
		tableCurrentItems[selectedIndex] = itemObjectToJson();
		addItemToLocalStorage();
		alert('Informações editadas.')
		operation = 'addItem';
		return true;
	}

	function itemObjectToJson() {
		let stringJson = '';

		for (let index = 0; index < arrayPropertyItemsJson.length; index++) {
			stringJson += "\"" + arrayPropertyItemsJson[index] + "\"" + ":" + "\"" + $(arrayValueItemsJson[index]).val() + "\"" + ",";
		}
		let objectJson = stringJson.substring(0, (stringJson.length - 1));
		stringJson = '{' + objectJson + '}';

		return stringJson;
	}

	function listItems() {
		let textHeadTableItemsPart1 = '<thead>teste<tr><th><img src=\'js/delete.png\' class=\'btnDeleteAll\'/></th>';
		let textHeadTableItemsPart2 = '</tr></thead><tbody></tbody>';

		for (let index = 0; index < arrayHeadTable.length; index++) {
			textHeadTableItemsPart1 += '<th>' + arrayHeadTable[index] + '</th>';
		}

		$('#tblListItems').html('');
		$('#tblListItems').html(textHeadTableItemsPart1 + textHeadTableItemsPart2);
		
		for (let itemJson of tableCurrentItems) {
			let item = JSON.parse(itemJson);
			let index = tableCurrentItems.indexOf(itemJson);
			let textValueItemsPart2 = '';
			
			let textValueItemsPart1 = '<tr><td><img src=\'js/edit.png\' alt=\'' + index + '\' class=\'btnEditItem\'/><img src=\'js/delete.png\' alt=\'' + index + '\' class=\'btnDeleteItem\'/></td>';

			for (let index = 0; index < arrayPropertyItemsJson.length; index++) {
				textValueItemsPart2 += '<td>' + item[arrayPropertyItemsJson[index]] + '</td>';
			}
			
			$('#tblListItems tbody').append(textValueItemsPart1 + textValueItemsPart2 + '</tr>');
		}
	}

	function deleteItem() {
		tableCurrentItems.splice(selectedIndex, 1);
		addItemToLocalStorage();
		alert('Registro excluído.');
	}

	function deleteAll() {
		tableCurrentItems = [];
		addItemToLocalStorage();
		console.log('Todos os itens foram excluídos.');
	}

	function getItemJson() {
		for (let item of tableCurrentItems) {
			let itemJson = JSON.parse(item);
			if (itemJson[arrayPropertyItemsJson[0]] == $(arrayValueItemsJson[0]).val()) {
				return itemJson;
			}
		}
	}

	function getNamePropertyJson(tableJson) {
		let arrayItemsRegistered = [];

		for (let item of tableJson) {
			let itemJson = JSON.parse(item);
			if (tableJson == tbLocalJobs) {
				arrayItemsRegistered.push(itemJson.JobName);
			} else if (tableJson == tbLocalProcess) {
				arrayItemsRegistered.push(itemJson.ProcessName);
			} else if (tableJson == tbLocalMaterials) {
				arrayItemsRegistered.push(itemJson.MaterialName);
			} else if (tableJson == tbLocalOutsourced) {
				arrayItemsRegistered.push(itemJson.OutsourcedName);
			}
		}
		return arrayItemsRegistered;
	}

	function getDatalistsToForm(tbLocalItems) {
		let allRegisteredItems = getNamePropertyJson(tbLocalItems);
		let textDatalistItems = [];

		for (let item of allRegisteredItems) {
			textDatalistItems += '<option value=' + item + '>';
		}
		
		return textDatalistItems;
	}

	function datalistsToForm() {
		let allRegisteredJobs = getDatalistsToForm(tbLocalJobs);
		let allRegisteredProcesses = getDatalistsToForm(tbLocalProcess);
		let allRegisteredMaterials = getDatalistsToForm(tbLocalMaterials);
		let allRegisteredOutsourced = getDatalistsToForm(tbLocalOutsourced);

		$('#dtlProductJob').html(allRegisteredJobs);
		$('#dtlProductProcess').html(allRegisteredProcesses);
		$('#dtlProductMaterial').html(allRegisteredMaterials);
		$('#dtlProductOutsourced').html(allRegisteredOutsourced);
	}

	datalistsToForm();
	listItems();

	$('#frmRegister').on('submit', function() {
		if (operation == 'addItem') {
			return addItemJson();
		} else {
			return editItemJson();
		}
	});

	$('#tblListItems').on('click', '.btnEditItem', function() {
		operation = 'editItem';
		selectedIndex = parseInt($(this).attr('alt'));
		
		let item = JSON.parse(tableCurrentItems[selectedIndex]);

		for (let index = 0; index < arrayValueItemsJson.length; index++) {
			$(arrayValueItemsJson[index]).val(item[arrayPropertyItemsJson[index]]);
		}

		$(arrayValueItemsJson[4]).focus();
	});

	$('#tblListItems').on('click', '.btnDeleteItem', function() {
		selectedIndex = parseInt($(this).attr('alt'));
		deleteItem();
		listItems();
	});

	$('#tblListItems').on('click', '.btnDeleteAll', function() {
		deleteAll();
		listItems();
	});

	let btnRegister = $('#btnRegister');
	btnRegister.on('click', function() {
		event.preventDefault();
		console.log(tableCurrentItems);
		
		let link = document.createElement('a');
		link.href = 'data:application/octet-stream;charset=utf-8,' + tableCurrentItems;
		link.download = nameFileSave;
		link.click();
	});

	let btnLoadFile = $('#btnLoadFile');
	btnLoadFile.bind("click", function() {
		event.preventDefault();
		let regex = /^([a-zA-Z0-9\s_\\.\-:])+(.json)$/;
		if (regex.test($("#fileUpload").val().toLowerCase())) {
			if (typeof(FileReader) != 'undefined') {
				let reader = new FileReader();
				reader.onload = function(file) {
					let fileRead = file.target.result;

					deleteAll();

					let newFileToMerge = '[' + fileRead + ']';
					newFileToMerge = JSON.parse(newFileToMerge);

					for (let index of newFileToMerge) {
						newFileToMerge[index] = JSON.stringify(index);
						tableCurrentItems.push(newFileToMerge[index]);
					}

					addItemToLocalStorage();
					console.log('Itens carregados para a lista atual.');

					listItems();
				}
				reader.readAsText($('#fileUpload')[0].files[0]);
			} else {
				alert('Este navegador não suporta HTML5.');
			}
		} else {
			alert('Por favor, carregue um arquivo JSON válido');
		}
	});
});
