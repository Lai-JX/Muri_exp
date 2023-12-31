from runtime.rpc_stubs.master_to_worker_pb2 import JobInfo

import subprocess
import os
import utils


class Task(object):
    def __init__(self, job_info: JobInfo, scheduler_ip, trace_name, this_dir) -> None:
        super().__init__()

        self._job_num = job_info.num                # job数
        self._node_id = list(job_info.node_id)      # 需要用到的node
        self._job_id = job_info.job_id              # list
        self._job_name = job_info.job_name          # list
        self._batch_size = job_info.batch_size      # list
        self._iterations = job_info.iterations      # list
        self._gpus = job_info.gpus                  # 第一个node的gpu_list
        self._scheduler_ip = scheduler_ip           # 即master_ip
        self._num_gpu = job_info.num_gpu            # 第一个job的gpu
        self._this_dir = this_dir
        self._job_counter = job_info.job_counter    # list
        self._trace_name = trace_name
    

    def get_idle_port(self):
        return 9013 + 2*min(self._node_id) + int(self._gpus.split(',')[0])      # ljx 每个节点只有两个2个gpu，所以这里先改为2
        # return utils.find_free_port()


    @staticmethod
    def test_kill_restart():
        bash_cmd = 'nvidia-smi; sleep 2m; date'
        return bash_cmd


    def real_job(self):
        bash_cmd = f'bash {self._this_dir}/workloads/run.sh'
        for i in range(self._job_num):
            # 设置job的参数，依次为model    batch-size    num-worker    prefetch-factor    train-dir    iters    job-id         iters为剩余迭代次数
            bash_cmd += f' {self._job_name[i]} {self._batch_size[i]} 0 2 -1 {self._iterations[i]} {self._job_id[i]} {self._job_counter[i]}' # 0、2、-1分别代表num_worker、prefetch_factor和train_dir
        bash_cmd += f' {self._num_gpu}'
        bash_cmd += f' --scheduler-ip {self._scheduler_ip}'
        bash_cmd += f' --trainer-port {self.get_idle_port()} --this-dir {self._this_dir}/workloads'
        return bash_cmd

    def run(self):
        bash_cmd = ''
        # if self._job_name == 'test_kill_restart':
        #     bash_cmd = self.test_kill_restart()
        # else:
        bash_cmd = self.real_job()

        cmd = bash_cmd.split()

        hostfile_dir = self._this_dir+'/workloads/hostfiles'
        assert os.path.exists(hostfile_dir)
        # hostfile_list = [f'worker-{node_id}\n' for node_id in self._node_id]    # ljx:需要改为从gpu1开始
        hostfile_list = [f'gpu{(node_id+1)} slots=2 port=6789\n' for node_id in self._node_id]                        # ljx:需要改为从gpu1开始,若以gpu1为server，记得去掉^3
        hostfile_list = hostfile_list[0:-1]                                                                             # ljx:需要改为从gpu1开始
        hostfile_list.append(f'gpu{(len(self._node_id))} slots={self._num_gpu-(len(self._node_id)-1)*2} port=6789')   # ljx:需要改为从gpu1开始,若以gpu1为server，记得去掉^3
        ch = '-'
        job_id_str = ch.join([str(x) for x in list(self._job_id)])
        job_counter_str = ch.join([str(x) for x in list(self._job_counter)])
        # print(self._iterations)
        with open(hostfile_dir+f'/hostfile-[{job_id_str}]-[{job_counter_str}]', 'w') as f:
            f.writelines(hostfile_list)
        utils.print_ljx("task.run:hostfile_list:", hostfile_list)
        utils.print_ljx("log path after here:",self.log_path, '\n')
        environ_dict = dict(os.environ)
        environ_dict['CUDA_VISIBLE_DEVICES'] = self._gpus
        with open(self.log_path, 'w+') as f:
            self._handler = subprocess.Popen(
                cmd, 
                stdout=f,
                stderr=f,               # 之后再改为f
                env=environ_dict,
            )

        return cmd
    

    def terminate(self):
        self._handler.terminate()
    
    def wait(self):
        self._handler.wait()
    

    @property
    def return_code(self):              # 检查进程是否终止，如果终止返回 returncode，否则返回 None
        return self._handler.poll()

    @property
    def pid(self):
        return self._handler.pid


    @property
    def log_path(self):
        # print('self._trace_name:',self._trace_name,os.path.exists(f'{self._trace_name}/'))
        # if not os.path.exists(f'{self._trace_name}/'):
        #     print(not os.path.exists(f'{self._trace_name}/'))
        #     os.makedirs(f'{self._trace_name}/')
        path = ''
        for i in range(self._job_num):
            if i==0:
                path = f'{self._trace_name}/{self._job_id[i]}-{self._job_counter[i]}-{self._job_name[i]}'
            else:
                path += f'_{self._job_id[i]}-{self._job_counter[i]}-{self._job_name[i]}'
        return path + '.txt'
