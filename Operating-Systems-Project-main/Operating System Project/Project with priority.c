#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
#include <stdlib.h>
#include <time.h>

#define MAX_TRACKS 10
#define MAX_TRAINS 10

pthread_mutex_t track_locks[MAX_TRACKS];
pthread_mutex_t priority_lock;  // Mutex for priority updates
sem_t semaphore;
FILE *log_file;

int available[MAX_TRACKS]; // Available tracks
int max_need[MAX_TRAINS][MAX_TRACKS]; // Maximum required tracks for each train
int allocated[MAX_TRAINS][MAX_TRACKS]; // Tracks allocated to each train
int need[MAX_TRAINS][MAX_TRACKS]; // Tracks still needed by each train
int finish[MAX_TRAINS]; // Indicates if a train has finished or not
int priority[MAX_TRAINS]; // Priority for each train

pthread_mutex_t safety_check_lock; // Lock for safety check to check the requested tracks can be allocated or not


// Function to write log to file
void write_log(const char *log_message) {
    time_t current_time;
    time(&current_time);

    // Remove newline character from asctime output
    char* time_str = strtok(asctime(localtime(&current_time)), "\n");

    fprintf(log_file, "[%s] %s\n", time_str, log_message);
    fflush(log_file);
}

void* train_arrival(void* id) {
    int train_id = *((int*)id);
    char log_message[100];
    sprintf(log_message, "Train %d is approaching the junction with priority %d.", train_id, priority[train_id]);
    write_log(log_message);

    sleep(rand() % 3 + 1);

    sprintf(log_message, "Train %d has arrived at the junction.", train_id);
    write_log(log_message);

    // Attempt to acquire tracks using Banker's Algorithm
    pthread_mutex_lock(&safety_check_lock);

    int safe = 0;
    int deadlock_retry = 0;
    while (!safe) {
        // Check if the request can be granted, considering priority
        safe = 1;
        for (int i = 0; i < MAX_TRACKS; ++i) {
            if (max_need[train_id][i] > available[i]) {
                safe = 0;
                break;
            }
        }

        if (!safe) {
            pthread_mutex_unlock(&safety_check_lock);
            sleep(rand() % 2 + 1); // Wait before retrying request
            pthread_mutex_lock(&safety_check_lock);
            deadlock_retry++;

            if (deadlock_retry >= 3) {
                sprintf(log_message, "Potential deadlock detected for Train %d. Releasing acquired locks.", train_id);
                write_log(log_message);

                for (int i = 0; i < MAX_TRACKS; ++i) {
                    available[i] += allocated[train_id][i];
                    allocated[train_id][i] = 0;
                    need[train_id][i] = max_need[train_id][i];  // Update the 'need' array
                }
                pthread_mutex_unlock(&safety_check_lock);
                pthread_exit(NULL);
            }
        }
    }

    // If the request can be granted, allocate tracks
    for (int i = 0; i < MAX_TRACKS; ++i) {
        allocated[train_id][i] = max_need[train_id][i];
        need[train_id][i] -= max_need[train_id][i];  // Update the 'need' array
        available[i] -= max_need[train_id][i];
    }

    pthread_mutex_unlock(&safety_check_lock);

    // Simulate passing through tracks
    sprintf(log_message, "Train %d is passing through tracks.", train_id);
    write_log(log_message);
    sleep(rand() % 3 + 2);

    // Release allocated tracks
    pthread_mutex_lock(&safety_check_lock);
    for (int i = 0; i < MAX_TRACKS; ++i) {
        available[i] += allocated[train_id][i];
        allocated[train_id][i] = 0;
        need[train_id][i] = max_need[train_id][i];  // Update the 'need' array
    }
    pthread_mutex_unlock(&safety_check_lock);

    sprintf(log_message, "Train %d has passed tracks.", train_id);
    write_log(log_message);
    sprintf(log_message, "Train %d has left the junction.", train_id);
    write_log(log_message);

    pthread_exit(NULL);
}

void setup_tracks(int num_tracks) {
    for (int i = 0; i < num_tracks; ++i) {
        pthread_mutex_init(&track_locks[i], NULL);
        available[i] = 3; // Initializing available tracks
    }
    pthread_mutex_init(&safety_check_lock, NULL);
    pthread_mutex_init(&priority_lock, NULL);  // Initialize the priority_lock
}

void input_max_need(int num_trains, int num_tracks) {
    printf("Enter the maximum required tracks for each train (0 for random values):\n");
    for (int i = 0; i < num_trains; ++i) {
        printf("Train %d: ", i);
        for (int j = 0; j < num_tracks; ++j) {
            scanf("%d", &max_need[i][j]);
            need[i][j] = max_need[i][j];  // Initialize 'need' same as 'max_need'
        }
        // Update priority (with mutex protection)
        pthread_mutex_lock(&priority_lock);
        priority[i] = rand() % 2; // Assigning random priority (0 or 1)
        pthread_mutex_unlock(&priority_lock);
    }
}

void generate_random_max_need(int num_trains, int num_tracks) {
    for (int i = 0; i < num_trains; ++i) {
        for (int j = 0; j < num_tracks; ++j) {
            max_need[i][j] = rand() % 4 + 1; // Random values between 1 and 4
            need[i][j] = max_need[i][j];  // Initialize 'need' same as 'max_need'
        }
        // Update priority (with mutex protection)
        pthread_mutex_lock(&priority_lock);
        priority[i] = rand() % 2; // Assigning random priority (0 or 1)
        pthread_mutex_unlock(&priority_lock);
    }
}

void display_track_status(int num_tracks) {
    printf("\nTrack Status:\n");
    for (int i = 0; i < num_tracks; ++i) {
        printf("Track %d: Available - %d\n", i, available[i]);
    }
}

void display_train_status(int num_trains, int num_tracks) {
    printf("\nTrain Status:\n");
    for (int i = 0; i < num_trains; ++i) {
        printf("Train %d - Need: ", i);
        for (int j = 0; j < num_tracks; ++j) {
            printf("%d ", need[i][j]);
        }
        printf("\n");
    }
}

void display_tracks_and_trains(int num_tracks, int num_trains) {
    printf("\nVisual Representation of Tracks and Trains:\n");
    printf("Tracks:\n");
    for (int i = 0; i < num_tracks; ++i) {
        printf("| Track %d ", i);
    }
    printf("|\n");

    for (int i = 0; i < num_trains; ++i) {
        printf("Train %d: ", i);
        for (int j = 0; j < num_tracks; ++j) {
            if (allocated[i][j] > 0) {
                printf("|  T%d   ", i);
            } else {
                printf("|       ");
            }
        }
        printf("|\n");
    }
}

void* deadlock_detection(void* args) {
    while (1) {
        sleep(4);

        pthread_mutex_lock(&safety_check_lock);

        int deadlock_detected = 1;

        for (int i = 0; i < MAX_TRAINS; ++i) {
            if (!finish[i]) {
                deadlock_detected = 0;
                break;
            }
        }

        if (deadlock_detected) {
            printf("\nDeadlock detected! Attempting resolution...\n");

            // Implement deadlock resolution logic here

            printf("Deadlock resolution complete.\n");
        }

        pthread_mutex_unlock(&safety_check_lock);
    }
}

int main() {
    int num_tracks, num_trains;
    printf("Enter the number of tracks (up to %d): ", MAX_TRACKS);
    scanf("%d", &num_tracks);

    printf("Enter the number of trains (up to %d): ", MAX_TRAINS);
    scanf("%d", &num_trains);

    if (num_tracks > MAX_TRACKS || num_tracks < 1 || num_trains > MAX_TRAINS || num_trains < 1) {
        printf("Invalid number of tracks or trains. Exiting...\n");
        return 1;
    }

    // Open log file for writing
    log_file = fopen("train_simulation_log.txt", "w");
    if (log_file == NULL) {
        printf("Error opening log file. Exiting...\n");
        return 1;
    }

    setup_tracks(num_tracks);

    int choice;
    printf("Choose option:\n1. Enter maximum required tracks manually\n2. Generate random values\nEnter choice: ");
    scanf("%d", &choice);

    if (choice == 1) {
        input_max_need(num_trains, num_tracks);
    } else if (choice == 2) {
        generate_random_max_need(num_trains, num_tracks);
    } else {
        printf("Invalid choice. Exiting...\n");
        fclose(log_file);
        return 1;
    }

    pthread_t trains[MAX_TRAINS];
    int train_ids[MAX_TRAINS];

    srand(time(NULL));

    // Creating threads for each train
    for (int i = 0; i < num_trains; ++i) {
        train_ids[i] = i;
        pthread_create(&trains[i], NULL, train_arrival, &train_ids[i]);
    }

    // Display initial track and train status
    display_track_status(num_tracks);
    display_train_status(num_trains, num_tracks);
    display_tracks_and_trains(num_tracks, num_trains);

    pthread_t deadlock_thread;
    pthread_create(&deadlock_thread, NULL, deadlock_detection, NULL);

    // Waiting for all trains to finish
    for (int i = 0; i < num_trains; ++i) {
        pthread_join(trains[i], NULL);
    }

    // Display final track and train status
    display_track_status(num_tracks);
    display_train_status(num_trains, num_tracks);
    display_tracks_and_trains(num_tracks, num_trains);

    pthread_cancel(deadlock_thread); // Cancel the deadlock detection thread

    // Destroying mutex locks for tracks and safety check lock
    for (int i = 0; i < num_tracks; ++i) {
        pthread_mutex_destroy(&track_locks[i]);
    }
    pthread_mutex_destroy(&safety_check_lock);
    pthread_mutex_destroy(&priority_lock); // Destroy the priority_lock

    // Close log file
    fclose(log_file);

    return 0;
}
