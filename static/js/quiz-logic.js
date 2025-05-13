document.addEventListener('DOMContentLoaded', function () {
    // 📌 Αρχικές μεταβλητές
    let score = 0;
    let angle = 0;
    let startTime = null;
    let pendingPoints = 0;
    let currentWinningSlice = null;
    let idleRotationInterval = null;

    const scoreDisplay = document.getElementById('score');
    const timerDisplay = document.getElementById('timer');
    const spinButton = document.getElementById('spinWheelBtn');
    const tickSound = new Audio('/static/sounds/wheel-tick.mp3');
    const questionBox = document.getElementById('questionBox');
    const quizData = JSON.parse(document.getElementById('game-container').getAttribute('data-quiz'));
    const questions = quizData.questions;
    let currentQuestionIndex = 0;

    tickSound.loop = true;
    tickSound.volume = 1;

    function startIdleRotation() {
        let idleAngle = 0;
        idleRotationInterval = setInterval(() => {
            idleAngle += 0.1; // πολύ αργή περιστροφή
            wheelSetup.wheelGroup.style.transform = `rotate(${idleAngle}deg)`;
        }, 20);
    }

    const timerInterval = setInterval(updateTimerDisplay, 1000);

    function updateTimerDisplay() {
        if (startTime) {
            const now = Date.now();
            const elapsed = Math.floor((now - startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            timerDisplay.textContent = `Time: ${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
    }

    spinButton.addEventListener('click', function () {
        if (!startTime) {
            startTime = Date.now();
        }

        if (idleRotationInterval) {
            clearInterval(idleRotationInterval);
            idleRotationInterval = null;
        }

        const spins = Math.floor(Math.random() * 3) + 3;
        const extraDegrees = Math.floor(Math.random() * 360);

        angle += spins * 360 + extraDegrees;
        tickSound.play();

        wheelSetup.wheelGroup.style.transform = `rotate(${angle}deg)`;

        setTimeout(() => {
            tickSound.pause();
            tickSound.currentTime = 0;

            const normalized = angle % 360;
            const sector = Math.floor((360 - normalized) / wheelSetup.sliceAngle);
            const pickedLabel = wheelSetup.labels[sector % wheelSetup.numberOfSlices];

            // Καθαρίζουμε προηγούμενα blink
            if (currentWinningSlice) {
                currentWinningSlice.classList.remove('slice-blink', 'slice-pop');
                currentWinningSlice = null;
            }

            wheelSetup.slices.forEach(slice => slice.classList.remove('slice-blink', 'slice-pop'));

            const winningSliceIndex = sector % wheelSetup.numberOfSlices;
            const winningSlice = wheelSetup.slices[winningSliceIndex];

            // Κάνουμε το σωστό slice να αναβοσβήνει
            currentWinningSlice = winningSlice;
            winningSlice.classList.add('slice-blink', 'slice-pop');

            scoreDisplay.classList.remove('bling', 'win', 'lose', 'bomb');

            if (pickedLabel === 'Bomb') {
                score = 0;
                if (score < 0) score = 0;
                scoreDisplay.classList.add('bomb');
                scoreDisplay.textContent = `Score: ${score}`;
                setTimeout(() => {
                    scoreDisplay.classList.remove('bomb');
                }, 1500);

                return; // Δεν εμφανίζουμε ερώτηση
            } else if (pickedLabel.startsWith('-')) {
                score -= Math.abs(parseInt(pickedLabel));
                if (score < 0) score = 0;
                scoreDisplay.classList.add('bling', 'lose');
                scoreDisplay.textContent = `Score: ${score}`;
                setTimeout(() => {
                    scoreDisplay.classList.remove('bling', 'lose');
                }, 1500);

                return; // Δεν εμφανίζουμε ερώτηση
            } else {
                // Θετικός αριθμός ➔ Περιμένουμε σωστή απάντηση
                pendingPoints = parseInt(pickedLabel);
                console.log(`Πρέπει να απαντήσει σωστά για +${pendingPoints} πόντους`);

                showNextQuestion();
            }
        }, 4000);
    });

    function showNextQuestion() {
        questionBox.innerHTML = '';
    
        if (currentQuestionIndex >= questions.length) {
            endGame();
            return;
        }
    
        const question = questions[currentQuestionIndex];
    
        const questionTitle = document.createElement('div');
        questionTitle.textContent = question.question_text;
        questionTitle.style.marginBottom = '20px';
        questionTitle.style.fontSize = '22px';
        questionBox.appendChild(questionTitle);
    
        // Δημιουργούμε wrapper για τα κουμπιά
        const optionsWrapper = document.createElement('div');
        optionsWrapper.classList.add('options-wrapper');
        questionBox.appendChild(optionsWrapper);
    
        if (question.question_type === 'multiple_choice') {
            question.options.forEach((option, index) => {
                if (option) {
                    const button = document.createElement('button');
                    button.textContent = option;
                    button.classList.add('answer-button');
                    button.setAttribute('data-value', (index + 1)); // index + 1 = 1,2,3,4
                    button.onclick = () => checkAnswer(index + 1, question.correct_answer);
                    optionsWrapper.appendChild(button);
                }
            });
        } else if (question.question_type === 'true_false') {
            ['True', 'False'].forEach(option => {
                const button = document.createElement('button');
                button.textContent = option;
                button.classList.add('answer-button');
                button.setAttribute('data-value', option.toLowerCase());
                button.onclick = () => checkAnswer(option.toLowerCase(), String(question.correct_answer).toLowerCase());
                optionsWrapper.appendChild(button);
            });
        }
    }
    

    function checkAnswer(selected, correct) {
        const allButtons = document.querySelectorAll('.answer-button');
        allButtons.forEach(btn => btn.disabled = true);

        if (currentWinningSlice) {
            currentWinningSlice.classList.remove('slice-blink', 'slice-pop');
            currentWinningSlice = null;
        }

        let isCorrect = false;

        if (typeof selected === 'number') {
            isCorrect = (selected === correct);
        } else {
            isCorrect = (selected === correct);
        }

        const correctButton = Array.from(allButtons).find(btn => {
            const btnValue = btn.getAttribute('data-value');
            if (typeof correct === 'number') {
                return Number(btnValue) === correct;
            } else {
                return btnValue === correct;
            }
        });

        const selectedButton = Array.from(allButtons).find(btn => {
            const btnValue = btn.getAttribute('data-value');
            if (typeof selected === 'number') {
                return Number(btnValue) === selected;
            } else {
                return btnValue === selected;
            }
        });

        if (isCorrect) {
            selectedButton.classList.add('correct');
            console.log("✅ Σωστή απάντηση!");
            score += pendingPoints;
            scoreDisplay.classList.add('bling', 'win');
        } else {
            selectedButton.classList.add('wrong');
            if (correctButton) {
                correctButton.classList.add('correct');
            }
            console.log("❌ Λάθος απάντηση!");
            scoreDisplay.classList.add('bling', 'lose');
        }

        pendingPoints = 0;
        scoreDisplay.textContent = `Score: ${score}`;

        setTimeout(() => {
            scoreDisplay.classList.remove('bling', 'win', 'lose');
            currentQuestionIndex++;

            // ✨ Μόλις απαντήσει, καθάρισε την ερώτηση
            questionBox.innerHTML = '<div>Spin the wheel</div>';

            if (currentQuestionIndex >= questions.length) {
                endGame();
            }
        }, 1500);
    }


    function endGame() {
        spinButton.disabled = true;
        clearInterval(timerInterval);
        const endTime = Date.now();
        const totalTime = Math.floor((endTime - startTime) / 1000);

        questionBox.innerHTML = `
            <div>🎉 Μπράβο! Τέλος παιχνιδιού!</div>
            <div>🕓 Χρόνος: ${Math.floor(totalTime / 60)}:${(totalTime % 60).toString().padStart(2, '0')}</div>
            <div>🏆 Σκορ: ${score}</div>
        `;
    }

    startIdleRotation();
});
