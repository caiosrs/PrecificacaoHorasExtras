// template/static/js/autocomplete.js

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('id_nome_funcionario');
    const suggestionsContainer = document.getElementById('autocomplete-suggestions');
    let currentFocus = -1; // Rastreia o item atualmente focado nas sugestões

    // Obter a lista de nomes do servidor
    const names = {{ names|safe }}; // Certifique-se de passar a lista de nomes do servidor para o template

    // Função para filtrar sugestões com base na entrada
    function getSuggestions(query) {
        return names.filter(name => name.toLowerCase().includes(query.toLowerCase()));
    }

    // Função para renderizar sugestões
    function renderSuggestions(suggestions) {
        suggestionsContainer.innerHTML = '';
        currentFocus = -1; // Resetar o foco ao renderizar novas sugestões
        suggestions.forEach((suggestion, index) => {
            const div = document.createElement('div');
            div.textContent = suggestion;
            div.classList.add('autocomplete-suggestion');
            div.addEventListener('click', () => {
                input.value = suggestion;
                suggestionsContainer.innerHTML = '';
            });
            div.addEventListener('mouseover', () => {
                currentFocus = index; // Atualizar o foco quando o mouse estiver sobre uma sugestão
                updateSuggestionHighlight();
            });
            suggestionsContainer.appendChild(div);
        });
    }

    // Função para atualizar o destaque das sugestões
    function updateSuggestionHighlight() {
        const items = suggestionsContainer.querySelectorAll('.autocomplete-suggestion');
        items.forEach((item, index) => {
            item.classList.toggle('highlight', index === currentFocus);
        });
    }

    // Adiciona o evento de input no campo de texto
    input.addEventListener('input', () => {
        const query = input.value;
        if (query.length >= 3) { // Mostra sugestões apenas após 3 letras
            const suggestions = getSuggestions(query);
            renderSuggestions(suggestions);
        } else {
            suggestionsContainer.innerHTML = '';
        }
    });

    // Navegar pelas sugestões com as setas do teclado
    input.addEventListener('keydown', (e) => {
        const items = suggestionsContainer.querySelectorAll('.autocomplete-suggestion');
        if (e.key === 'ArrowDown') {
            currentFocus++;
            updateSuggestionHighlight();
            if (currentFocus >= items.length) currentFocus = 0;
            input.value = items[currentFocus] ? items[currentFocus].textContent : '';
        } else if (e.key === 'ArrowUp') {
            currentFocus--;
            updateSuggestionHighlight();
            if (currentFocus < 0) currentFocus = items.length - 1;
            input.value = items[currentFocus] ? items[currentFocus].textContent : '';
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (currentFocus > -1) {
                input.value = items[currentFocus].textContent;
                suggestionsContainer.innerHTML = '';
            }
        }
    });

    // Fecha sugestões ao clicar fora
    document.addEventListener('click', (e) => {
        if (!e.target.closest('#id_nome_funcionario') && !e.target.closest('#autocomplete-suggestions')) {
            suggestionsContainer.innerHTML = '';
        }
    });
});