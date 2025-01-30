#!/root/.cache/pypoetry/virtualenvs/zfs-backup-HY1fGE8C-py3.12/bin/python
import paramiko
import getpass
from subprocess import check_output, Popen, PIPE, DEVNULL
import shlex


def get_latest_snapshot():
    latest_snapshot = check_output(
        "zfs list -t snapshot -o name -s creation | tail -1",
        shell=True,
        stderr=DEVNULL,
    ).decode().strip()
    if not latest_snapshot:
        return latest_snapshot
    _, snapshot = latest_snapshot.split('@')
    snapshot = f'dockerz/docker@{snapshot}'
    return snapshot


def load_ssh_config(filepath='/home/violet/.ssh/config') -> paramiko.SSHConfig:
    config = paramiko.SSHConfig.from_path("/home/violet/.ssh/config")
    return config


def connect_msi() -> paramiko.SSHClient:
    config = load_ssh_config()

    msi = config.lookup('msi')
    hostname = msi['hostname']
    username = msi['user']

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, key_filename='/home/violet/.ssh/id_rsa')
    return client


def send_receive_snapshot():
    bufsize = 1024
    # incremental update, if there's already an
    # existing old version of this dataset.
    stale_snapshot = get_latest_snapshot()
    stale_snapshot = ['-i', stale_snapshot] if stale_snapshot else []

    msi: paramiko.SSHClient = connect_msi()

    _, stdout, _ = msi.exec_command('zfs list -t snapshot -o name -s creation | tail -1')
    recent_remote_snapshot = stdout.read().decode().strip()
    print('recent remote snapshot:', recent_remote_snapshot)

    zfs_send_command = ['sudo', '-S', 'zfs', 'send'] + stale_snapshot + [recent_remote_snapshot]
    zfs_send_command = shlex.join(zfs_send_command)
    print('command:', zfs_send_command)

    zfs_send_stdin, zfs_send_stdout, zfs_send_stderr = msi.exec_command(zfs_send_command, bufsize=bufsize)

    zfs_send_stdin.write(f"{getpass.getpass()}\n")
    zfs_send_stdin.flush()
    print('wrote password to remote')

    pv_proc = Popen(['pv'], stdin=PIPE, stdout=PIPE)
    # TODO: -F option
    receive_proc = Popen(["zfs", "receive", "dockerz2"], stdin=pv_proc.stdout)
    print('zfs receive dockerz2: receiving chunks')

    while True:
        chunk = zfs_send_stdout.read(bufsize)
        pv_proc.stdin.write(chunk)
        pv_proc.stdin.flush()
        if len(chunk) < bufsize:
            break

    print(f'done writing chunks, waiting for receiver to complete')
    receive_proc.wait()

    print("finished zfs receive")

    msi.close()


if __name__ == "__main__":
    send_receive_snapshot()


