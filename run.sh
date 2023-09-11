#!/bin/bash
# Note: Due to the scripts are highly related to intracompany platform, 
#we only demonstrate the functionality and show the pseudocode of the 
#related scripts (e.g., run.sh, prepare_env.sh). Please adjust to your 
#platform if you would like to execute the testbed experiment.
echo -e "ljx:run.sh\n"

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# set the worker ip and port
SCHEDULER_IP=$1
shift
WORKER_PORT=$1
shift
TRAINER_PORT=$1
shift
WORKER_ID=$1
shift

# prepare environment before start, takes several minutes
cd $THIS_DIR
bash $THIS_DIR/prepare_env.sh $SCHEDULER_IP $WORKER_PORT $TRAINER_PORT $WORKER_ID

# set the scheduling policy and related parameters
placement=('yarn')
export schedules_all=$1
shift
jobs=('cluster_trace')
setups=("n4g4")
packing_nums=("4")
schedule_intervals=("360")          # 6分钟（和论文中一致）
fast_forwards=("60")

IFS=','
read -ra schedule <<<"$schedules_all"

mkdir $THIS_DIR/results
for setup in ${setups[@]};do                                                                            # 集群配置
    cluster_spec="cluster_specs/${setup}.csv"
    for job in ${jobs[@]};do                                                                            # job集
        job_file="trace-data/${job}.csv"
        for packing_num in ${packing_nums[@]};do                                                        # 一个node的job数量
            for schedule_interval in ${schedule_intervals[@]};do                                        # 调度的时间间隔
                for fast_forward in ${fast_forwards[@]};do                                              # fast_forward
                    trace_name="${setup}j${job}p${packing_num}si${schedule_interval}ff${fast_forward}"
                    log_folder="results/${trace_name}"                                                      # results/n4g4jcluster_tracep4si360ff60
                    mkdir $THIS_DIR/${log_folder}
                    for p in ${placement[@]};do                                                         # placement 策略
                        for s in ${schedule[@]};do
                            log_name="${log_folder}/${s}-${p}-${packing_num}"                               # run.py的log path: results/n4g4jcluster_tracep4si360ff60/dlas-gpu-yarn-4
                            mkdir $THIS_DIR/$log_name
                            job_log="$THIS_DIR/job_logs/${trace_name}/${s}-${p}-${packing_num}"             # worker.py的log path: job_logs/clusster_trace/dlas-gpu-yarn-4
                            rm -rf $job_log
                            echo "running..." $setup $job $s
                            if [ $WORKER_ID -eq 1 ]; then
                                # start scheduler for the main node
                                echo -e '\nstart scheduler for the main node\n'
                                python $THIS_DIR/run.py --cluster_spec=$THIS_DIR/${cluster_spec} --print --scheme=${p} --trace_file=$THIS_DIR/${job_file} --schedule=${s} --log_path=$THIS_DIR/${log_name} --packing_num ${packing_num} --schedule_interval ${schedule_interval} --fast_forwarding ${fast_forward} & # >$THIS_DIR/${log_name}/scheduler.out &   # ljx
                                sleep 10s
                            else
                                # sleep 6m    # ljx
                                sleep 10s
                            fi

                            # start worker for all nodes. 这里only one node?! → 根据WORKER_ID来指定
                            echo -e '\nstart worker\n'
                            python $THIS_DIR/worker.py --master_ip $SCHEDULER_IP --worker_port $WORKER_PORT --trace_name ${job_log} --this-dir ${THIS_DIR} $arg & # >$THIS_DIR/${log_name}/worker.out &     # ljx

                            wait

                            # get the results after execution
                            echo "calcing..." $setup $job $s
                            if [ $WORKER_ID -eq 1 ]; then
                                python $THIS_DIR/calc.py $THIS_DIR/${log_name} >$THIS_DIR/${log_name}/result.out
                            else
                                sleep 2m
                            fi
                        done
                    done
                done
            done
        done
    done
done

                