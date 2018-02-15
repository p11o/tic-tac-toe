const HOST = 'http://localhost:8888';

const boardTemplate = board => {
    return `
        <table>
            <tbody>
                <tr>
                    <td data-coord="[0,0]">${board[0][0]}</td>
                    <td data-coord="[0,1]">${board[0][1]}</td>
                    <td data-coord="[0,2]">${board[0][2]}</td>
                </tr>
                <tr>
                    <td data-coord="[1,0]">${board[1][0]}</td>
                    <td data-coord="[1,1]">${board[1][1]}</td>
                    <td data-coord="[1,2]">${board[1][2]}</td>
                </tr>
                <tr>
                    <td data-coord="[2,0]">${board[2][0]}</td>
                    <td data-coord="[2,1]">${board[2][1]}</td>
                    <td data-coord="[2,2]">${board[2][2]}</td>
                </tr>
            </tbody>
        </table>
    `;
};

const renderBoard = board => {
    const $board = document.querySelector('#board');
    board = JSON.parse(JSON.stringify(board).replace(/0/g, '""'));
    board = JSON.parse(JSON.stringify(board).replace(/1/g, '"O"'));
    board = JSON.parse(JSON.stringify(board).replace(/2/g, '"X"'));
    $board.innerHTML = boardTemplate(board);
};

const fetchBoard = () => {
    return fetch(`${HOST}/game`).then(
        res => res.json()
    );
};

const sendMove = coords => {
    return fetch(`${HOST}/client/move`, {
        method: 'PUT',
        body: `{"coords":${coords}}`
    }).then(res => res.json());
};

const fetchRobotMove = () => {
    return fetch(`${HOST}/robot/move`, {
        method: 'PUT'
    }).then(res => res.json());
};

const createNewGame = () => {
    return fetch(`${HOST}/game`, { method: 'POST' }).then(res => res.json());
}

const main = () => {
    fetchBoard().then(({board}) => renderBoard(board));
    document.body.addEventListener('click', e => {
        const $target = e.target;
        if ($target.matches('td') && $target.textContent == '') {
            $target.textContent = 'X';
            fetchBoard().then(({over}) => {
                if (!over) {
                    return sendMove(
                        $target.getAttribute('data-coord')
                    ).then(({board, over}) => {
                       if (!over) {
                           return fetchRobotMove().then(({board}) => {
                               return renderBoard(board);
                           });
                        }
                    });
                }
            }).catch(e => {
                console.error(e);
                alert(e.message);
            });
        }
    });

    document.body.addEventListener('click', e => {
        const $target = e.target;
        if ($target.matches('.new')) {
            createNewGame().then(({board}) => renderBoard(board));
        }
    });

    document.body.addEventListener('click', e => {
        const $target = e.target;
        if ($target.matches('.cpu')) {
            fetchRobotMove().then(({board}) => {
                return renderBoard(board);
            });
        }
    });
};

main();
