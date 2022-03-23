$(function() {
	let operation = 'addItem';
	let selectedIndex = -1;
	let tableCurrentItems = [];
	let nameFileSave = '';
	let arrayPropertyItemsJson = [];
	let arrayValueItemsJson = [];
	let arrayHeadTable = [];
	let listItemsOfLocalStorage = [];

	let getHtmlFile = $('meta[name=\'description\']').attr('content');

	if (getHtmlFile == 'htmlMaterials') {
		listItemsOfLocalStorage = 'tbMaterials';
		nameFileSave = 'lista_materiais.json';

		arrayPropertyItemsJson = ['MaterialID', 'MaterialName', 'MaterialLength', 'MaterialWidth', 'MaterialThickness', 'MaterialDiameter', 'MaterialGrammage', 'MaterialColor', 'MaterialStock', 'MaterialProvider', 'MaterialCost', 'MaterialLeadtime'];
		arrayValueItemsJson = ['#txtMaterialID', '#txtMaterialName', '#txtMaterialLength', '#txtMaterialWidth', '#txtMaterialThickness', '#txtMaterialDiameter', '#txtMaterialGrammage', '#txtMaterialColor', '#txtMaterialStock', '#txtMaterialProvider', '#txtMaterialCost', '#txtMaterialLeadtime'];
		arrayHeadTable = ['ID', 'Nome', 'Compr.', 'Larg.', 'Espes.', 'Diâm.', 'Gr.', 'Cor', 'Estoque', 'Forn.', 'Custo', 'Leadtime'];
	} else if (getHtmlFile == 'htmlResources') {
		listItemsOfLocalStorage = 'tbResources';
		nameFileSave = 'lista_recursos.json';

		arrayPropertyItemsJson = ['ResourceID', 'ResourceName', 'ResourceHourType', 'ResourceSectors', 'ResourceGroups', 'ResourceCostCenter', 'ResourceJourney'];
		arrayValueItemsJson = ['#txtResourceID', '#txtResourceName', '#txtResourceHourType', '#txtResourceSectors', '#txtResourceGroups', '#txtResourceCostCenter', '#txtResourceJourney'];
		arrayHeadTable = ['ID', 'Nome', 'Tipo de hora', 'Setor', 'Grupo', 'Centro de custos', 'Jornada'];
	} else if (getHtmlFile == 'htmlProcess') {
		listItemsOfLocalStorage = 'tbProcess';
		nameFileSave = 'lista_processos.json';

		arrayPropertyItemsJson = ['ProcessID', 'ProcessName', 'ProcessHourType', 'ProcessProductionStep', 'ProcessResourceGroups', 'ProcessResources', 'ProcessAllocationProperties', 'ProcessAggregationProperties'];
		arrayValueItemsJson = ['#txtProcessID', '#txtProcessName', '#txtProcessHourType', '#txtProcessProductionStep', '#txtProcessResourceGroups', '#txtProcessResources', '#txtProcessAllocationProperties', '#txtProcessAggregationProperties'];
		arrayHeadTable = ['ID', 'Nome', 'Tipo hora', 'Etapa produção', 'Grupo recursos', 'Recurso', 'Prop alocação', 'Prop agregação'];
	} else if (getHtmlFile == 'htmlOutsourced') {
		listItemsOfLocalStorage = 'tbOutsourced';
		nameFileSave = 'lista_terceirizados.json';

		arrayPropertyItemsJson = ['OutsourcedID', 'OutsourcedName', 'OutsourcedMEC', 'OutsourcedLeadtime', 'OutsourcedRuntime'];
		arrayValueItemsJson = ['#txtOutsourcedID', '#txtOutsourcedName', '#txtOutsourcedMEC', '#txtOutsourcedLeadtime', '#txtOutsourcedRuntime'];
		arrayHeadTable = ['ID', 'Fornecedor', 'MEC', 'Leadtime', 'Prazo execução'];
	} else if (getHtmlFile == 'htmlJobs') {
		listItemsOfLocalStorage = 'tbJobs';
		nameFileSave = 'lista_jobs.json';

		arrayPropertyItemsJson = ['JobID', 'JobName', 'JobClient', 'JobNecessity'];
		arrayValueItemsJson = ['#txtJobID', '#txtJobName', '#txtJobClient', '#txtJobNecessity'];
		arrayHeadTable = ['ID', 'Job', 'Cliente', 'Necessidade'];
	}

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

		$(arrayValueItemsJson[0]).attr('readonly','readonly');
		$(arrayValueItemsJson[1]).focus();
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
