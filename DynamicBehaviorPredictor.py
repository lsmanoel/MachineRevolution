import tensorflow as tf
import numpy as np
import threading


class DynamicBehaviorPredictor:
    def __init__(self,
                 surface_size,
                 num_input=2,
                 input_length=100,
                 num_outputs=2,
                 num_neurons=100,
                 batch_size=1,
                 learning_rate=0.001,
                 num_y_pred_output=10):

        self.service_status = 'offline'

        self.surface_size = surface_size
        self.num_input = num_input
        self.input_length = input_length
        self.num_outputs = num_outputs
        self.output_length = input_length
        self.num_neurons = num_neurons
        self.batch_size = batch_size
        self.learning_rate = learning_rate

        self.y_true_print = [[self.surface_size[0]//2, self.surface_size[1]//2]]*self.input_length
        self.y_true_print = np.asarray(self.y_true_print).reshape(-1, self.input_length, self.num_outputs)

        self.y_print = [[self.surface_size[0]//2, self.surface_size[1]//2]]*self.input_length
        self.y_print = np.asarray(self.y_print).reshape(-1, self.input_length, self.num_outputs)

        self.x_input = [[[self.surface_size[0]//2, self.surface_size[1]//2]]]
        self.y_true_input = [[[self.surface_size[0]//2, self.surface_size[1]//2]]]
        self.y_pred_output = np.zeros(self.output_length)
        self.num_y_pred_output = num_y_pred_output

        self.update_model = False
        self.load_model = False
        self.close_app = False
        self.received_data = False
        self.clear_data_buffer = False

        self.model_file_name = "./untitled_rnn_player_behavior_model"
        self.train_and_predict_thread_handler = threading.Thread(target=self.train_and_predict_thread)

    def start_train_and_predict_thread(self, model_file_name=None):
        if model_file_name is not None:
            self.model_file_name = model_file_name
        self.train_and_predict_thread_handler.start()

    def train_and_predict_thread(self):
        # --------------------------------------------------------------------------------------------------------------
        x = tf.placeholder(tf.float32, [None,
                                        self.input_length,
                                        self.num_input])

        y_true = tf.placeholder(tf.float32, [None,
                                             self.output_length,
                                             self.num_outputs])

        cell = tf.contrib.rnn.OutputProjectionWrapper(
            tf.nn.rnn_cell.BasicRNNCell(num_units=self.num_neurons,
                                        activation=tf.nn.selu),
            output_size=self.num_outputs)

        y, states = tf.nn.dynamic_rnn(cell, x, dtype=tf.float32)

        loss = tf.reduce_mean(tf.square(y - y_true))  # MSE
        optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate)
        train = optimizer.minimize(loss)

        init = tf.global_variables_initializer()

        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.75)

        saver = tf.train.Saver()
        # --------------------------------------------------------------------------------------------------------------

        with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options)) as sess:
            sess.run(init)
            print("init train_thread...")
            x_input_buffer = [[self.surface_size[0]//2, self.surface_size[1]//2]]*self.input_length
            y_input_buffer = [[self.surface_size[0]//2, self.surface_size[1]//2]]*self.input_length

            self.service_status = 'online'

            while not self.close_app:
                # ======================================================================================================
                if self.update_model is True:
                    saver.save(sess, self.model_file_name)  # "./rnn_time_series_model"

                if self.received_data is True:
                    self.received_data = False

                    if self.clear_data_buffer is True:
                        self.clear_data_buffer = False
                        x_input_buffer = [[self.surface_size[0]//2, self.surface_size[1]//2]]*self.input_length
                        y_input_buffer = [[self.surface_size[0]//2, self.surface_size[1]//2]]*self.input_length

                    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    # train:
                    x_input_buffer_array = np.asarray(x_input_buffer).reshape(-1, self.input_length, self.num_input)

                    y_input_buffer.append(self.x_input)
                    del y_input_buffer[0]
                    y_input_buffer_array = np.asarray(y_input_buffer).reshape(-1, self.input_length, self.num_outputs)

                    # --------------------------------------------------------------------------------------------------
                    _, loss_value = sess.run(
                        [train, loss],
                        feed_dict={x: x_input_buffer_array,
                                   y_true: y_input_buffer_array})
                    # --------------------------------------------------------------------------------------------------

                    x_input_buffer.append(self.x_input)
                    del x_input_buffer[0]

                    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    # predict:
                    buffer_array = y_input_buffer_array

                    for _ in range(self.num_y_pred_output):
                        self.y_print = sess.run(y, feed_dict={x: buffer_array})
                        buffer_array = self.y_print
                # ======================================================================================================

    def set_data_to_train(self, input_data):
        self.x_input = input_data
        self.y_true_input = input_data
        self.received_data = True

    @property
    def x_input(self):
        return self._x_input

    @x_input.setter
    def x_input(self, value):
        self._x_input = value
        self.received_data = True













